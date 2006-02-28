from zope.interface import implements, classProvides
from nevow import rend, loaders, util
from webut.navi import inavi
from demoplugins import idemo, container

class QuuxPage(rend.Page):
    implements(inavi.INavigationElement)

    title = 'Quux!'

    docFactory = loaders.xmlfile(util.resource_filename('demoplugins', 'quux.html'))

    def render_navigation(self, ctx, data):
        return ctx.tag.clear()[idemo.IDemoNavigation(ctx)]

class Quux(object):
    classProvides(container.IDemoContainerPlugin)

    name = "quux"

    def getResource(klass, ctx):
        return QuuxPage()
    getResource = classmethod(getResource)
