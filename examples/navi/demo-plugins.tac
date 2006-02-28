import sys, os
from zope.interface import implements
from twisted.internet import defer
from twisted.application import service, strports
from twisted.python import util, log
from nevow import appserver, inevow, url, rend, loaders, tags
from webut.navi import inavi, naviplugin

sys.path.append(os.path.dirname(__file__))

from demoplugins import idemo
import demoplugins

class Menu(rend.Fragment):
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'menu.html'),
                                 pattern='menu')


    def __init__(self, original, url=None):
        super(Menu, self).__init__(original)
        self.url = url

    def data_url(self, ctx, data):
        return self.url

    def data_title(self, ctx, data):
        info = inavi.INavigationElement(self.original, None)
        if info is not None:
            title = info.title
        else:
            title = str(self.original)
        return title

    def render_menu(self, ctx, data):
        name, resource = data
        return ctx.tag.clear()[Menu(resource, self.url.child(name))]

    def render_if(self, ctx, data):
        r=ctx.tag.allPatterns(str(bool(data)))
        return ctx.tag.clear()[r]

    def data_children(self, ctx, data):
        navi = inavi.INavigable(self.original, None)
        if navi is None:
            return []
        d = navi.getChildren(ctx)
        return d

class Root(naviplugin.PluggableNavigation):
    implements(inevow.IResource)

    interface = idemo.IDemoPlugin

    package = demoplugins

    def renderHTTP(self, ctx):
        return url.here.child('')

    def locateChild(self, ctx, segments):
        u = url.URL.fromContext(ctx)
        ctx.remember(Menu(self, u), idemo.IDemoNavigation)
        return super(Root, self).locateChild(ctx, segments)

root = Root()
application = service.Application("demo-plugins")
site = appserver.NevowSite(root)
svc = strports.service("8080", site)
svc.setServiceParent(application)
