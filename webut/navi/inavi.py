from zope.interface import Interface, Attribute
from twisted import plugin

class INavigable(Interface):
    """
    A navigable resource.

    Normally, an INavigable should also implement IResource.

    The biggest requirement for navigability is the ability
    to list the child resources.
    """

    def listChildren(ctx):
        """
        List children.

        Note that you are given no guarantees that locateChild will be
        able to find all these children, and vice versa locateChild
        may find children not listed here. See getChildren for that.

        @return: a Deferred list names of the children.
        """

    def getChildren(ctx):
        """
        Get children.

        Note that you are given no guarantees that a locateChild ran
        at a later time will be able to find all these children, and
        vice versa locateChild may find children not listed here. But
        as they are returned at the same time, the results are valid
        *right now*.

        @return: a Deferred list of tuples [ (name, IResource), ... ]
        """

    def locateChild(ctx, segments):
        """
        See C{nevow.inevow.IResource.locateChild}.
        """

class INavigationPlugin(plugin.IPlugin):
    """
    A twisted plugin to be loaded as part of the resource tree.

    To have plugins on multiple levels, use subclasses to categorize
    the plugins.
    """

    name = Attribute("""
    Path segment where to place this plugin.

    This is a single segment, relative to whatever parent loaded the
    plugin.
    """)

    def getResource(ctx):
        """
        Returns an Deferred that will result in IResource or None.

        IResources may additionally have attributes
        title and description.
        """
        pass

    # optional
    priority = Attribute("""
    Priority for sorting plugins in navigation.

    Defaults to 50.
    """)

class INavigationElement(Interface):
    title = Attribute("""
    Title of the element, for use in links and such. At most a few words.
    """)

    description = Attribute("""
    Short description of the element, for tooltips etc. About one sentence.
    """)
