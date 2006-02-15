from zope.interface import Interface, Attribute
from nevow import inevow

class ISkinnable(inevow.IResource, inevow.IRenderer):
    """
    A skinnable web resource.

    Note that ISkinnable's must implement IRenderer too. Fragment and
    Page already do this, but if you implement IResource from scratch,
    be sure to add that.

    IRenderer.rend should return the resource's content, without the
    <html>, <head> or <body> elements, from the renderer
    'content'. There are additional attributes for better integration
    into navigational elements.
    """

    title = Attribute("""
    Title of the application.

    May be displayed in HTML <title> tag or some other header.
    """)

    stylesheets = Attribute("""
    Sequence of filenames to include as CSS stylesheets.
    """)

class ISkinInfo(Interface):
    """
    Information passed to a skin.
    """

    content = Attribute("""An ISkinnable to be skinned.""")

    pathToFiles = Attribute("""
    A nevow.url.URL that points to the topmost instance of this skin.

    Useful for referring to skin-specific auxiliary files, such as
    images and CSS.
    """)
