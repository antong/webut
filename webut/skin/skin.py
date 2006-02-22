from zope.interface import implements
from twisted.internet import defer
from nevow import inevow, url, tags
from nevow.flat.twist import deferflatten
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
        if skinnable is not None:
            skin = self.skinFactory(self)
            assert iskin.ISkin.providedBy(skin), \
                   "Skin %r does not provide ISkin" % skin
            origRenderer = self.resource.renderer
            def render_skin(ctx, data):
                content = inevow.IQ(ctx.tag).onePattern('skincontent')
                gather = tags.invisible()
                d = deferflatten(content, ctx, gather.__getitem__)
                def gotContent(s):
                    self.content = gather
                    return skin
                d.addCallback(gotContent)
                return d
            def renderer(ctx, name):
                if name == 'skin':
                    return render_skin
                else:
                    return origRenderer(ctx, name)
            self.resource.renderer = renderer
        return inevow.IResource(self.resource).renderHTTP(ctx)

class DebugSkinner(Skinner):
    def __init__(self, *a, **kw):
        super(DebugSkinner, self).__init__(*a, **kw)
        self._skinFactory = self.skinFactory
        self.skinFactory = self.debugSkinFactory

    def debugSkinFactory(self, *a, **kw):
        skin = self._skinFactory(*a, **kw)
        from zope.interface import verify as ziverify
        ziverify.verifyObject(iskin.ISkin, skin)
        iskin.ISkin.validateInvariants(skin)
        return skin
