#!/usr/bin/python
import os
from distutils.core import setup
from distutils import sysconfig

if __name__=='__main__':
    setup(name="webut",
	  description="Miscellaneous utilities for nevow and twisted.web{,2} programming",
	  long_description="""

A collection of utility libraries for use when programming web
applications with nevow, twisted.web and twisted.web2.

The intent is that as the individual libraries stabilize, they can be
moved to nevow or twisted.web2.

Current content:
 - support library for skinnable web apps
 - web app navigation library

""".strip(),
	  author="Tommi Virtanen",
	  author_email="tv@inoi.fi",
	  url="http://www.inoi.fi/open/trac/webut",
	  license="X11",

	  packages=[
	"webut",
	"webut.skin",
	"webut.skin.test",
	"webut.navi",
	],
          )
