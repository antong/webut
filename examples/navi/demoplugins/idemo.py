from zope.interface import Interface
from webut.navi import inavi

class IDemoNavigation(Interface):
    """
    Marker interface to look up the top of the navigation data.
    """

class IDemoPlugin(inavi.INavigationPlugin):
    """
    Navigation plugins used by the demo implement this interface.
    """
