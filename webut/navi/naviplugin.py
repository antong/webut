from zope.interface import implements
from twisted.internet import defer
from twisted.python import log
from twisted import plugin
from nevow import url
from webut.navi import inavi

class PluggableNavigation(object):
    """
    A pluggable navigation element.

    Please subclass and set these attributes:

    - interface

    - package

    interface should be a subclass of inavi.INavigationPlugin.
    """

    interface = None
    package = None

    implements(inavi.INavigable)

    def _getPlugins(self):
        assert self.interface is not None, \
                   'Interface must be set in %r' % self
        assert issubclass(self.interface, inavi.INavigationPlugin), \
               'Interface must subclass INavigationPlugin in %r' % self
        assert self.package is not None, \
               'Package must be set in %r' % self
        return plugin.getPlugins(self.interface, self.package)

    def listChildren(self, ctx):
        d = self.getChildren(ctx)
        def cb(children):
            for name, resource in children:
                yield name
        d.addCallback(cb)
        d.addCallback(list)
        return d

    def _sortChildren(self, children):
        l = [(getattr(plug, 'priority', 50), plug.name, plug)
             for plug in children]
        l.sort()
        return [plug for (pri, name, plug) in l]

    def getChildren(self, ctx):
        """
        Get all children.

        @return: Deferred that will results in a list of tuples
        [ (name, IResource), ... ]
        """
        return defer.maybeDeferred(self._getChildren, ctx)

    def _getChildren(self, ctx):
        def f():
            plugs = self._sortChildren(self._getPlugins())
            for plug in plugs:
                d = defer.maybeDeferred(plug.getResource, ctx)
                d.addErrback(log.err)
                def mangle(resource, name):
                    return (name, resource)
                d.addCallback(mangle, plug.name)
                yield d
        d = defer.gatherResults(list(f()))
        def cb(results):
            for name, resource in results:
                if resource is not None:
                    yield name, resource
        d.addCallback(cb)
        d.addCallback(list)
        return d

    def _locateChild(self, children, ctx, segments):
        if segments[0] == '':
            # choose the first plugin
            for name, resource in children:
                return url.here.child(name), segments[1:]

            # don't let plugins rule the '' name,
            # that's too confusing
            return None, ()

        for name, resource in children:
            if segments[0] == name:
                return resource, segments[1:]

        return None, ()

    def locateChild(self, ctx, segments):
        d = self.getChildren(ctx)
        d.addCallback(self._locateChild, ctx, segments)
        return d
