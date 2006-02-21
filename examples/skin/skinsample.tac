from zope.interface import implements
import random
from twisted.application import service, strports
from twisted.python import util
from nevow import appserver, loaders, rend
from webut.skin import iskin, skin

class Content(rend.Page):
    implements(iskin.ISkinnable)
    addSlash = True
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'content.html'),
                                 pattern='thecontent')

    title = 'Greeting'

    def render_cruelity(self, ctx, data):
        return ctx.tag.clear()[random.choice(['Cruel', 'Sweet', ''])]

class Color(rend.Page):
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'color-skin.html'))

    def data_title(self, ctx, data):
        return self.original.content.title

    def render_background(self, ctx, data):
        return ctx.tag(style='background-color: #00%02x00;' % random.randint(128,255))

    def render_content(self, ctx, data):
        return self.original.content

class Boxed(rend.Page):
    docFactory = loaders.xmlfile(util.sibpath(__file__, 'boxed-skin.html'))

    def data_title(self, ctx, data):
        return self.original.content.title

    def render_content(self, ctx, data):
        return self.original.content


content = Content()
root = skin.Skinner(Color, content)
## root = skin.Skinner(Boxed, content)

application = service.Application("skinsample")
site = appserver.NevowSite(root)
svc = strports.service("8080", site)
svc.setServiceParent(application)
