#!/usr/bin/env python
# coding:utf-8
# Author:  mozman
# Purpose: drawing
# Created: 10.09.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
"""
The *Drawing* object is the overall container for all SVG
elements. It provides the methods to store the drawing into a file or a
file-like object. If you want to use stylesheets, the reference links
to this stylesheets were also stored (`add_stylesheet`)
in the *Drawing* object.

set/get SVG attributes::

    element['attribute'] = value
    value = element['attribute']

The Drawing object also includes a defs section, add elements to the defs
section by::

    drawing.defs.add(element)

"""
from __future__ import unicode_literals

try:
    import unzip_requirements
except ImportError:
    pass

from svgwrite.container import SVG
from svgwrite.elementfactory import ElementFactory
from svgwrite.utils import pretty_xml
from s3 import save_svg
from colors import DEFAULT_COLORS


class Drawing(SVG, ElementFactory):
    """ This is the SVG drawing represented by the top level *svg* element.

    A drawing consists of any number of SVG elements contained within the drawing
    element, stored in the *elements* attribute.

    A drawing can range from an empty drawing (i.e., no content inside of the drawing),
    to a very simple drawing containing a single SVG element such as a *rect*,
    to a complex, deeply nested collection of container elements and graphics elements.
    """

    def __init__(self, filename="no_name.svg", size=('100%', '100%'), bg_color=DEFAULT_COLORS['bg_color'], **extra):
        """
        :param string filename: filesystem filename valid for :func:`open`
        :param 2-tuple size: width, height
        :param bg_color: hex code
        :param keywords extra: additional svg-attributes for the *SVG* object

        Important (and not SVG Attributes) **extra** parameters:

        :param string profile: ``'tiny | full'`` - define the SVG baseProfile
        :param bool debug: switch validation on/off

        """
        super(Drawing, self).__init__(size=size, **extra)
        self.filename = filename
        self.bg_color = bg_color
        self._stylesheets = []  # list of stylesheets appended

    def get_xml(self):
        """ Get the XML representation as `ElementTree` object.

        :return: XML `ElementTree` of this object and all its subelements

        """
        profile = self.profile
        version = self.version
        self.attribs['xmlns'] = "http://www.w3.org/2000/svg"
        self.attribs['xmlns:xlink'] = "http://www.w3.org/1999/xlink"
        self.attribs['xmlns:ev'] = "http://www.w3.org/2001/xml-events"

        self.attribs['baseProfile'] = profile
        self.attribs['version'] = version
        self.attribs['style'] = 'background-color: %s;' % self.bg_color
        return super(Drawing, self).get_xml()

    def add_stylesheet(self, href, title, alternate="no", media="screen"):
        """ Add a stylesheet reference.

        :param string href: link to stylesheet <URI>
        :param string title: name of stylesheet
        :param string alternate: ``'yes'|'no'``
        :param string media: ``'all | aureal | braille | embossed | handheld | print | projection | screen | tty | tv'``

        """
        self._stylesheets.append((href, title, alternate, media))

    def write_str(self, pretty=False):
        """ Write XML string
        :param pretty: True for easy readable output
        Python 3.x - set encoding at the open command::
        """
        arr = []
        # write xml header
        arr.append('<?xml version="1.0" encoding="utf-8" ?>\n')

        # don't use DOCTYPE. It's useless. see also:
        # http://tech.groups.yahoo.com/group/svg-developers/message/48562
        # write stylesheets
        stylesheet_template = '<?xml-stylesheet href="%s" type="text/css" ' \
                              'title="%s" alternate="%s" media="%s"?>\n'
        # removed map(), does not work with Python 3
        for stylesheet in self._stylesheets:
            arr.append(stylesheet_template % stylesheet)

        xml_string = self.tostring()
        if pretty:  # write easy readable XML file
            xml_string = pretty_xml(xml_string)
        arr.append(xml_string)
        return arr

    def save_str(self, pretty=False):
        try:
            arr = self.write_str(pretty=pretty)
            return ''.join(arr)
        except Exception as e:
            raise e

    def save_to_s3(self, checksum=None, pretty=False):
        try:
            xml_string = ''.join(self.write_str(pretty=pretty))
            return save_svg(xml_string, checksum)
        except Exception as e:
            raise e
