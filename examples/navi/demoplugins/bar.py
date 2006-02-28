from zope.interface import implements, classProvides
from nevow import rend, loaders, util
from webut.navi import inavi
from demoplugins import idemo

class BarPage(rend.Page):
    implements(inavi.INavigationElement)

    title = 'Bar!'

    docFactory = loaders.xmlfile(util.resource_filename('demoplugins', 'bar.html'))

    def render_navigation(self, ctx, data):
        return ctx.tag.clear()[idemo.IDemoNavigation(ctx)]

class Bar(object):
    classProvides(idemo.IDemoPlugin)

    name = "bar"

    priority = 10

    def getResource(klass, ctx):
        return BarPage()
    getResource = classmethod(getResource)
