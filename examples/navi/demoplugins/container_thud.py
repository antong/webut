from zope.interface import implements, classProvides
from nevow import rend, loaders, util
from webut.navi import inavi
from demoplugins import idemo, container

class ThudPage(rend.Page):
    implements(inavi.INavigationElement)

    title = 'Thud!'

    docFactory = loaders.xmlfile(util.resource_filename('demoplugins', 'thud.html'))

    def render_navigation(self, ctx, data):
        return ctx.tag.clear()[idemo.IDemoNavigation(ctx)]

class Thud(object):
    classProvides(container.IDemoContainerPlugin)

    name = "thud"

    def getResource(klass, ctx):
        return ThudPage()
    getResource = classmethod(getResource)
