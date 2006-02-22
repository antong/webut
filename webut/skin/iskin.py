from zope.interface import Interface, Attribute
from nevow import inevow

class ISkinnable(inevow.IResource, inevow.IRendererFactory):
    """
    A skinnable web resource.

    The topmost HTML element must render itself with the renderer
    'skin'. The renderer method of ISkinnable will be overridden to
    handle the 'skin' renderer properly.

    The resource's content, without the <html>, <head> or <body>
    elements, must be marked with the template 'skincontent'.

    The same ISkinnable must not be rendered twice, use a new instance
    instead. (There is a race condition in case the same instance is
    rendered simultaneusly.)

    There are additional attributes for better integration into
    navigational elements.
    """

    title = Attribute("""
    Title of the application.

    May be displayed in HTML <title> tag or some other header.
    """)

    stylesheets = Attribute("""
    Sequence of filenames to include as CSS stylesheets.
    """)

class ISkin(inevow.IRenderer):
    """
    A skin that knows how to wrap generic chunks of HTML.
    """

class ISkinInfo(Interface):
    """
    Information passed to a skin.
    """

    resource = Attribute("""An ISkinnable to be skinned.""")

    content = Attribute("""Flattened stan to be embedded in the page.""")

    pathToFiles = Attribute("""
    A nevow.url.URL that points to the topmost instance of this skin.

    Useful for referring to skin-specific auxiliary files, such as
    images and CSS.
    """)
