from zope.interface import implements, classProvides
from nevow import inevow, url
from webut.navi import naviplugin, inavi
from demoplugins import idemo
import demoplugins

class IDemoContainerPlugin(inavi.INavigationPlugin):
    pass

class ContainerPage(naviplugin.PluggableNavigation):
    implements(inevow.IResource)

    interface = IDemoContainerPlugin

    package = demoplugins

    def renderHTTP(self, ctx):
        return url.here.child('')

class Container(object):
    classProvides(idemo.IDemoPlugin)

    name = "container"

    def getResource(klass, ctx):
        return ContainerPage()
    getResource = classmethod(getResource)
