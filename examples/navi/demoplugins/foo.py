from zope.interface import implements, classProvides
from twisted.internet import address
from nevow import inevow, rend, loaders, util, url
from webut.navi import inavi
from demoplugins import idemo

class FooPage(rend.Page):
    implements(inavi.INavigationElement)

    title = 'Foo!'

    docFactory = loaders.xmlfile(util.resource_filename('demoplugins', 'foo.html'))

    def render_navigation(self, ctx, data):
        return ctx.tag.clear()[idemo.IDemoNavigation(ctx)]

    def render_visible(self, ctx, data):
        u = url.URL.fromContext(ctx)
        netloc = u.netloc.split(':', 1)
        netloc[0] = '127.0.0.1'
        u.netloc = ':'.join(netloc)
        return u

    def render_invisible(self, ctx, data):
        u = url.URL.fromContext(ctx).parentdir()
        netloc = u.netloc.split(':', 1)
        netloc[0] = '127.0.0.2'
        u.netloc = ':'.join(netloc)
        return u

class Foo(object):
    classProvides(idemo.IDemoPlugin)

    name = "foo"

    priority = 20

    def getResource(klass, ctx):
        # demonstrate conditional plugins by only being visible on
        # IP addresses that are odd. Use 127.0.0.1 vs 127.0.0.2
        # to see the difference.
        addr = inevow.IRequest(ctx).getHost()
        if (isinstance(addr, address.IPv4Address)
            and int(addr.host.split('.')[-1])%2==0):
            return None

        return FooPage()
    getResource = classmethod(getResource)
