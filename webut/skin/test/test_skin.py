from twisted.trial import unittest
from zope.interface import implements
from cStringIO import StringIO
from twisted.internet import defer
from nevow import inevow, tags, flat, context, rend, loaders, static
from webut.skin import iskin, skin

class Skin(object):
    implements(iskin.ISkin)
    def __init__(self, original):
        self.original = original
    def rend(self, ctx, data):
        return tags.invisible['[skin]', self.original.content, '[/skin]']
    def locateChild(self, ctx, segments):
        return None, ()

class FakeRequest(object):
    method = 'GET'
    def __init__(self, segments):
        self.segments = segments
        self.uri = (self.prePathURL() + '/junk/junk/junk?junk=remove')
        self._written = []
        self.args = {}
        self._sentHeaders = []

    def prePathURL(self):
        return 'http://fake.invalid/?junk=prepathjunk'

    def write(self, data):
        self._written.append(data)

    def setHeader(self, header, content):
        self._sentHeaders.append((header, content))

class Xyzzy(rend.Page):
    implements(iskin.ISkinnable)

    docFactory = loaders.stan(tags.invisible(render=tags.directive('skin'))[
        tags.invisible(pattern='skincontent')['xyzzy'],
        ])

class DeferredXyzzy(rend.Page):
    implements(iskin.ISkinnable)

    docFactory = loaders.stan(tags.invisible(render=tags.directive('skin'))[
        tags.invisible(pattern='skincontent', render=tags.directive('foo')),
        ])

    def render_foo(self, ctx, data):
        return defer.succeed('dyddy')

class ManyXyzzys(rend.Page):
    implements(iskin.ISkinnable)

    docFactory = loaders.stan(tags.invisible(render=tags.directive('skin'))[
        tags.invisible(pattern='skincontent', render=tags.directive('name')),
        ])

    def __init__(self, _name=None):
        super(ManyXyzzys, self).__init__()
        self.name = _name
        if self.name is None:
            self.name = 'topmost'

    def render_name(self, ctx, data):
        return self.name

    def locateChild(self, ctx, segments):
        return (self.__class__('%s.%s' % (self.name, segments[0])),
                segments[1:])

class Childish(object):
    implements(inevow.IResource)
    def locateChild(self, ctx, segments):
        child = getattr(self, 'child_%s' % segments[0], None)
        if child is None:
            return None, ()
        else:
            return child(), segments[1:]

class AuxFileSkin(rend.Page):
    implements(iskin.ISkin)
    def __init__(self, *a, **kw):
        super(AuxFileSkin, self).__init__(*a, **kw)
        self.putChild('test.css', static.Data('/* not real css */', 'text/css'))
    def rend(self, ctx, data):
        return loaders.stan(tags.invisible[
            '[skin css=', self.original.pathToFiles.child('test.css'), ']',
            self.original.content,
            '[/skin]',
            ])

class SkinTest(unittest.TestCase):
    def flatten(self, stan, ctx):
        output = StringIO()
        def finisher(s):
            output.write(s)
            return output.getvalue()
        d = flat.flattenFactory(stan, ctx, output.write, finisher)
        return d

    def context(self, resource, segments):
        ctx = context.PageContext(tag=resource)
        ctx.remember(resource, inevow.IData)
        ctx.remember(FakeRequest(segments), inevow.IRequest)
        return ctx

    def render(self, resource, ctx):
        d = defer.maybeDeferred(resource.renderHTTP, ctx)
        d.addCallback(self.flatten, ctx)
        def join(data, ctx):
            return ''.join(inevow.IRequest(ctx)._written + [data])
        d.addCallback(join, ctx)
        return d

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

    def locate(self, resource, segments, ctx=None):
        if ctx is None:
            ctx = self.context(resource, segments)
            ctx.remember((), inevow.ICurrentSegments)
        resource = inevow.IResource(resource)
        if segments:
            segments = tuple(segments)
            d = defer.maybeDeferred(resource.locateChild, ctx, segments)
            d.addCallback(self._undefer_locateChild)
        else:
            d = defer.succeed((resource, []))
        def cb(result):
            resource, segs = result

            prepath = list(inevow.ICurrentSegments(ctx))
            prepath.extend(segments[: len(segments) - len(segs)])
            ctx.remember(tuple(prepath), inevow.ICurrentSegments)
            if resource is None:
                assert not segs
                return (None, ctx)
            elif segs:
                return self.locate(resource, segments[1:], ctx=ctx)
            else:
                return (resource, ctx)
        d.addCallback(cb)
        return d

    def process(self, resource, segments):
        d = self.locate(resource, segments)
        def cb(result):
            resource, ctx = result
            d = self.render(resource, ctx)
            return d
        d.addCallback(cb)
        return d

    def test_simple(self):
        a = Xyzzy()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, [])
        def verify(got):
            self.assertEquals(got, '[skin]xyzzy[/skin]')
        d.addCallback(verify)
        return d

    def test_deferred(self):
        a = DeferredXyzzy()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, [])
        def verify(got):
            self.assertEquals(got, '[skin]dyddy[/skin]')
        d.addCallback(verify)
        return d

    def test_childWithSkin_topmost(self):
        a = ManyXyzzys()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, [])
        def verify(got):
            self.assertEquals(got, '[skin]topmost[/skin]')
        d.addCallback(verify)
        return d

    def test_childWithSkin_one(self):
        a = ManyXyzzys()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, ['foo'])
        def verify(got):
            self.assertEquals(got, '[skin]topmost.foo[/skin]')
        d.addCallback(verify)
        return d

    def test_childWithSkin_two(self):
        a = ManyXyzzys()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, ['foo', 'bar'])
        def verify(got):
            self.assertEquals(got, '[skin]topmost.foo.bar[/skin]')
        d.addCallback(verify)
        return d

    def test_childWithoutSkin_toplevel(self):
        class MockPage(object):
            implements(inevow.IResource)
            def locateChild(self, ctx, segments):
                if segments[0] == 'foo':
                    return ManyXyzzys(), segments[1:]
                raise RuntimeError('Test should never get here.')
            def renderHTTP(self, ctx):
                return 'mockpage'

        a = MockPage()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, [])
        def verify(got):
            self.assertEquals(got, 'mockpage')
        d.addCallback(verify)
        return d

    def test_childWithoutSkin_one(self):
        class MockPage(object):
            implements(inevow.IResource)
            def locateChild(self, ctx, segments):
                if segments[0] == 'thud':
                    return ManyXyzzys(), segments[1:]
                raise RuntimeError('Test should never get here.')
            def renderHTTP(self, ctx):
                return 'mockpage'

        a = MockPage()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, ['thud'])
        def verify(got):
            self.assertEquals(got, '[skin]topmost[/skin]')
        d.addCallback(verify)
        return d

    def test_childWithoutSkin_two(self):
        class MockPage(object):
            implements(inevow.IResource)
            def locateChild(self, ctx, segments):
                if segments[0] == 'thud':
                    return ManyXyzzys(), segments[1:]
                raise RuntimeError('Test should never get here.')
            def renderHTTP(self, ctx):
                return 'mockpage'

        a = MockPage()
        r = skin.DebugSkinner(Skin, a)
        d = self.process(r, ['thud', 'quux'])
        def verify(got):
            self.assertEquals(got, '[skin]topmost.quux[/skin]')
        d.addCallback(verify)
        return d

    def test_pathToFiles_top(self):
        a = Childish()
        a.child_blah = lambda : skin.DebugSkinner(AuxFileSkin, ManyXyzzys())
        d = self.process(a, ['blah'])
        def verify(got):
            self.assertEquals(got, '[skin css=http://fake.invalid/blah/test.css]topmost[/skin]')
        d.addCallback(verify)

        d.addCallback(lambda dummy: self.process(a, ['blah', 'test.css']))
        def compare(got):
            self.assertEquals(got, '/* not real css */')
        d.addCallback(compare)
        return d

    def test_pathToFiles_top_dir(self):
        a = Childish()
        a.child_blah = lambda : skin.DebugSkinner(AuxFileSkin, ManyXyzzys())
        d = self.process(a, ['blah', ''])
        def verify(got):
            self.assertEquals(got, '[skin css=http://fake.invalid/blah/test.css]topmost.[/skin]')
        d.addCallback(verify)

        d.addCallback(lambda dummy: self.process(a, ['blah', 'test.css']))
        def compare(got):
            self.assertEquals(got, '/* not real css */')
        d.addCallback(compare)
        return d

    def test_pathToFiles_one(self):
        a = Childish()
        a.child_blah = lambda : skin.DebugSkinner(AuxFileSkin, ManyXyzzys())
        d = self.process(a, ['blah', 'foo'])
        def verify(got):
            self.assertEquals(got, '[skin css=http://fake.invalid/blah/test.css]topmost.foo[/skin]')
        d.addCallback(verify)

        d.addCallback(lambda dummy: self.process(a, ['blah', 'test.css']))
        def compare(got):
            self.assertEquals(got, '/* not real css */')
        d.addCallback(compare)
        return d

    def test_pathToFiles_two(self):
        a = Childish()
        a.child_blah = lambda : skin.DebugSkinner(AuxFileSkin, ManyXyzzys())
        d = self.process(a, ['blah', 'foo', 'baz'])
        def verify(got):
            self.assertEquals(got, '[skin css=http://fake.invalid/blah/test.css]topmost.foo.baz[/skin]')
        d.addCallback(verify)

        d.addCallback(lambda dummy: self.process(a, ['blah', 'test.css']))
        def compare(got):
            self.assertEquals(got, '/* not real css */')
        d.addCallback(compare)
        return d

class ConfigurableLookup(unittest.TestCase):
    def test_simple(self):
        class Confable(rend.Page):
            implements(iskin.ISkinnable)
            def locateConfigurable(self, ctx, name):
                return ('Confable.locateConfigurable', ctx, name)
        a = Confable()
        r = skin.DebugSkinner(Skin, a)
        c = r.locateConfigurable('foo', 'bar')
        self.assertEquals(c, ('Confable.locateConfigurable', 'foo', 'bar'))
