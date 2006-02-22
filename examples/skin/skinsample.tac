from zope.interface import implements
import random
from twisted.application import service, strports
from twisted.python import util
from nevow import appserver, loaders, rend, inevow, url
from webut.skin import iskin, skin

class Content(rend.Page):
    implements(iskin.ISkinnable)
    addSlash = True
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'content.html'),
                                 pattern='skincontent')

    title = 'Greeting'

    def render_cruelity(self, ctx, data):
        return ctx.tag.clear()[random.choice(['Cruel', 'Sweet', ''])]

class Color(rend.Page):
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'color-skin.html'))

    def data_title(self, ctx, data):
        return self.original.content.title

    def render_background(self, ctx, data):
        return ctx.tag(style='color: white; background-color: #00%02x00;'
                       % random.randint(128,255))

    def render_content(self, ctx, data):
        return self.original.content

class Boxed(rend.Page):
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'boxed-skin.html'))

    def data_title(self, ctx, data):
        return self.original.content.title

    def render_content(self, ctx, data):
        return self.original.content


class Root(object):
    implements(inevow.IResource)
    def renderHTTP(self, ctx):
        return url.here.child('color')
    def locateChild(self, ctx, segments):
        content = Content()
        if segments[0] == '':
            return self, segments[1:]
        elif segments[0] == 'color':
            return skin.Skinner(Color, content), segments[1:]
        elif segments[0] == 'boxed':
            return skin.Skinner(Boxed, content), segments[1:]
        else:
            return None, ()

root = Root()
application = service.Application("skinsample")
site = appserver.NevowSite(root)
svc = strports.service("8080", site)
svc.setServiceParent(application)
