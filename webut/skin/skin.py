from zope.interface import implements
from twisted.internet import defer
from nevow import inevow, url
from webut.skin import iskin

class Skinner(object):
    implements(inevow.IResource, iskin.ISkinInfo)

    pathToFiles = None

    def __init__(self,
                 skinFactory,
                 resource,
                 pathToFiles=None):
        self.skinFactory = skinFactory
        self.resource = resource
        if pathToFiles is not None:
            self.pathToFiles = pathToFiles

    def _undefer_locateChild(self, result):
        """
        locateChild can return Deferred or (d, segs), handle the latter.
        """
        res, segs = result
        if isinstance(res, defer.Deferred):
            def cb(res, segs):
                return (res, segs)
            res.addCallback(cb, segs)
            return res
        else:
            return (res, segs)

    def locateChild(self, ctx, segments):
        d = defer.maybeDeferred(inevow.IResource(self.resource).locateChild, ctx, segments)
        d.addCallback(self._undefer_locateChild)
        d.addCallback(self._cb_locateChild_1, ctx, segments)
        return d

    def _cb_locateChild_1(self, result, ctx, segments):
        res, segs = result
        if res is None:
            return (res, segs)

        pathToFiles = self.pathToFiles
        if pathToFiles is None:
            pathToFiles = url.URL.fromContext(ctx).clear()
            for seg in inevow.ICurrentSegments(ctx):
                pathToFiles = pathToFiles.child(seg)
        res = self.__class__(skinFactory=self.skinFactory,
                             resource=res,
                             pathToFiles=pathToFiles)
        return (res, segs)

    def renderHTTP(self, ctx):
        if self.pathToFiles is None:
            pathToFiles = url.URL.fromContext(ctx).clear()
            for seg in inevow.ICurrentSegments(ctx):
                pathToFiles = pathToFiles.child(seg)
            self.pathToFiles = pathToFiles
        skinnable = iskin.ISkinnable(self.resource, None)
        if skinnable is None:
            return self.resource.renderHTTP(ctx)
        else:
            skin = self.skinFactory(self)
            return skin.renderHTTP(ctx)
