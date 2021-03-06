from __future__ import division, absolute_import, print_function

try:
    import unzip_requirements
except ImportError:
    pass
"""This submodule contains tools for creating svg files from paths and path
segments."""

# External dependencies:
from math import ceil
from custom_drawing import Drawing
from svgwrite import text as txt
from warnings import warn
from colors import DEFAULT_COLORS

# Internal dependencies
from svgpathtools import Path, Line, is_path_segment

# Used to convert a string colors (identified by single chars) to a list.
color_dict = {'a': 'aqua',
              'b': 'blue',
              'c': 'cyan',
              'd': 'darkblue',
              'e': '',
              'f': '',
              'g': 'green',
              'h': '',
              'i': '',
              'j': '',
              'k': 'black',
              'l': 'lime',
              'm': 'magenta',
              'n': 'brown',
              'o': 'orange',
              'p': 'pink',
              'q': 'turquoise',
              'r': 'red',
              's': 'salmon',
              't': 'tan',
              'u': 'purple',
              'v': 'violet',
              'w': 'white',
              'x': '',
              'y': 'yellow',
              'z': 'azure'}


def str2colorlist(s, default_color=None):
    color_list = [color_dict[ch] for ch in s]
    if default_color:
        for idx, c in enumerate(color_list):
            if not c:
                color_list[idx] = default_color
    return color_list


def is3tuple(c):
    return isinstance(c, tuple) and len(c) == 3


def big_bounding_box(paths_n_stuff):
    """Finds a BB containing a collection of paths, Bezier path segments, and
    points (given as complex numbers)."""
    bbs = []
    for thing in paths_n_stuff:
        if is_path_segment(thing) or isinstance(thing, Path):
            bbs.append(thing.bbox())
        elif isinstance(thing, complex):
            bbs.append((thing.real, thing.real, thing.imag, thing.imag))
        else:
            try:
                complexthing = complex(thing)
                bbs.append((complexthing.real, complexthing.real,
                            complexthing.imag, complexthing.imag))
            except ValueError:
                raise TypeError(
                    "paths_n_stuff can only contains Path, CubicBezier, "
                    "QuadraticBezier, Line, and complex objects.")
    xmins, xmaxs, ymins, ymaxs = list(zip(*bbs))
    xmin = min(xmins)
    xmax = max(xmaxs)
    ymin = min(ymins)
    ymax = max(ymaxs)
    return xmin, xmax, ymin, ymax


def davis_disvg(paths=None, colors=None, stroke_widths=None, nodes=None,
                node_colors=None, node_radii=None, margin_size=0.1,
                mindim=2000, dimensions=None, viewbox=None,
                text=None, text_path=None, font_size=None,
                attributes=None, svg_attributes=None, checksum=None, bg_color=DEFAULT_COLORS['bg_color']):
    """Takes in a list of paths and creates an SVG file containing said paths.
    REQUIRED INPUTS:
        :param paths - a list of paths

    OPTIONAL INPUT:
        :param colors - specifies the path stroke color.  By default all paths
        will be black (#000000).  This paramater can be input in a few ways
        1) a list of strings that will be input into the path elements stroke
            attribute (so anything that is understood by the svg viewer).
        2) a string of single character colors -- e.g. setting colors='rrr' is
            equivalent to setting colors=['red', 'red', 'red'] (see the
            'color_dict' dictionary above for a list of possibilities).
        3) a list of rgb 3-tuples -- e.g. colors = [(255, 0, 0), ...].

        :param stroke_widths - a list of stroke_widths to use for paths
        (default is 0.5% of the SVG's width or length)

        :param nodes - a list of points to draw as filled-in circles

        :param node_colors - a list of colors to use for the nodes (by default
        nodes will be red)

        :param node_radii - a list of radii to use for the nodes (by default
        nodes will be radius will be 1 percent of the svg's width/length)

        :param text - string or list of strings to be displayed

        :param text_path - if text is a list, then this should be a list of
        path (or path segments of the same length.  Note: the path must be
        long enough to display the text or the text will be cropped by the svg
        viewer.

        :param font_size - a single float of list of floats.

        :param margin_size - The min margin (empty area framing the collection
        of paths) size used for creating the canvas and background of the SVG.

        :param mindim - The minimum dimension (height or width) of the output
        SVG (default is 600).

        :param dimensions - The display dimensions of the output SVG.  Using
        this will override the mindim parameter.

        :param viewbox - This specifies what rectangular patch of R^2 will be
        viewable through the outputSVG.  It should be input in the form
        (min_x, min_y, width, height).  This is different from the display
        dimension of the svg, which can be set through mindim or dimensions.

        :param attributes - a list of dictionaries of attributes for the input
        paths.  Note: This will override any other conflicting settings.

        :param svg_attributes - a dictionary of attributes for output svg.
        Note 1: This will override any other conflicting settings.
        Note 2: Setting `svg_attributes={'debug': False}` may result in a
        significant increase in speed.

        :param checksum - a string to be used for the filename, or None
        If None, a checksum will be generated here

        :param bg_color - a hex code applied to the SVG. Defaults to white (#FFF)

    NOTES:
        -The unit of length here is assumed to be pixels in all variables.

        -If this function is used multiple times in quick succession to
        display multiple SVGs (all using the default filename), the
        svgviewer/browser will likely fail to load some of the SVGs in time.
        To fix this, use the timestamp attribute, or give the files unique
        names, or use a pause command (e.g. time.sleep(1)) between uses.
    """

    try:
        _default_relative_node_radius = 5e-3
        _default_relative_stroke_width = 1e-3
        _default_path_color = DEFAULT_COLORS['color']  # black
        _default_node_color = DEFAULT_COLORS['node_colors']  # red
        _default_font_size = 12

        # check paths and colors are set
        if isinstance(paths, Path) or is_path_segment(paths):
            paths = [paths]
        if paths:
            if not colors:
                colors = [_default_path_color] * len(paths)
            else:
                assert len(colors) == len(paths)
                if isinstance(colors, str):
                    colors = str2colorlist(colors,
                                           default_color=_default_path_color)
                elif isinstance(colors, list):
                    for idx, c in enumerate(colors):
                        if is3tuple(c):
                            colors[idx] = "rgb" + str(c)

        # check nodes and nodes_colors are set (node_radii are set later)
        if nodes:
            if not node_colors:
                node_colors = [_default_node_color] * len(nodes)
            else:
                assert len(node_colors) == len(nodes)
                if isinstance(node_colors, str):
                    node_colors = str2colorlist(node_colors,
                                                default_color=_default_node_color)
                elif isinstance(node_colors, list):
                    for idx, c in enumerate(node_colors):
                        if is3tuple(c):
                            node_colors[idx] = "rgb" + str(c)

        # set up the viewBox and display dimensions of the output SVG
        # along the way, set stroke_widths and node_radii if not provided
        assert paths or nodes
        stuff2bound = []
        if viewbox:
            szx, szy = viewbox[2:4]
        else:
            if paths:
                stuff2bound += paths
            if nodes:
                stuff2bound += nodes
            if text_path:
                stuff2bound += text_path
            xmin, xmax, ymin, ymax = big_bounding_box(stuff2bound)
            dx = xmax - xmin
            dy = ymax - ymin

            if dx == 0:
                dx = 1
            if dy == 0:
                dy = 1

            # determine stroke_widths to use (if not provided) and max_stroke_width
            if paths:
                if not stroke_widths:
                    sw = max(dx, dy) * _default_relative_stroke_width
                    stroke_widths = [sw] * len(paths)
                    max_stroke_width = sw
                else:
                    assert len(paths) == len(stroke_widths)
                    max_stroke_width = max(stroke_widths)
            else:
                max_stroke_width = 0

            # determine node_radii to use (if not provided) and max_node_diameter
            if nodes:
                if not node_radii:
                    r = max(dx, dy) * _default_relative_node_radius
                    node_radii = [r] * len(nodes)
                    max_node_diameter = 2 * r
                else:
                    assert len(nodes) == len(node_radii)
                    max_node_diameter = 2 * max(node_radii)
            else:
                max_node_diameter = 0

            extra_space_for_style = max(max_stroke_width, max_node_diameter)
            xmin -= margin_size * dx + extra_space_for_style / 2
            ymin -= margin_size * dy + extra_space_for_style / 2
            dx += 2 * margin_size * dx + extra_space_for_style
            dy += 2 * margin_size * dy + extra_space_for_style
            viewbox = "%s %s %s %s" % (xmin, ymin, dx, dy)
            if dimensions:
                szx, szy = dimensions
            else:
                if dx > dy:
                    szx = str(mindim) + 'px'
                    szy = str(int(ceil(mindim * dy / dx))) + 'px'
                else:
                    szx = str(int(ceil(mindim * dx / dy))) + 'px'
                    szy = str(mindim) + 'px'

        # Create an SVG file
        if svg_attributes:
            dwg = Drawing(filename='no_name.svg', bg_color=bg_color, **svg_attributes)
        else:
            dwg = Drawing(filename='no_name.svg', size=(szx, szy), bg_color=bg_color, viewBox=viewbox)

        # add paths
        if paths:
            for i, p in enumerate(paths):
                if isinstance(p, Path):
                    ps = p.d()
                elif is_path_segment(p):
                    ps = Path(p).d()
                else:  # assume this path, p, was input as a Path d-string
                    ps = p

                if attributes:
                    good_attribs = {'d': ps}
                    for key in attributes[i]:
                        val = attributes[i][key]
                        if key != 'd':
                            try:
                                dwg.path(ps, **{key: val})
                                good_attribs.update({key: val})
                            except Exception as e:
                                warn(str(e))

                    dwg.add(dwg.path(**good_attribs))
                else:
                    dwg.add(dwg.path(ps, stroke=colors[i],
                                     stroke_width=str(stroke_widths[i]),
                                     fill='none'))

        # add nodes (filled in circles)
        if nodes:
            for i_pt, pt in enumerate([(z.real, z.imag) for z in nodes]):
                dwg.add(dwg.circle(pt, node_radii[i_pt], fill=node_colors[i_pt]))

        # add texts
        if text:
            assert isinstance(text, str) or (isinstance(text, list) and
                                             isinstance(text_path, list) and
                                             len(text_path) == len(text))
            if isinstance(text, str):
                text = [text]
                if not font_size:
                    font_size = [_default_font_size]
                if not text_path:
                    pos = complex(xmin + margin_size * dx, ymin + margin_size * dy)
                    text_path = [Line(pos, pos + 1).d()]
            else:
                if font_size:
                    if isinstance(font_size, list):
                        assert len(font_size) == len(text)
                    else:
                        font_size = [font_size] * len(text)
                else:
                    font_size = [_default_font_size] * len(text)
            for idx, s in enumerate(text):
                p = text_path[idx]
                if isinstance(p, Path):
                    ps = p.d()
                elif is_path_segment(p):
                    ps = Path(p).d()
                else:  # assume this path, p, was input as a Path d-string
                    ps = p

                # paragraph = dwg.add(dwg.g(font_size=font_size[idx]))
                # paragraph.add(dwg.textPath(ps, s))
                pathid = 'tp' + str(idx)
                dwg.defs.add(dwg.path(d=ps, id=pathid))
                txter = dwg.add(dwg.text('', font_size=font_size[idx]))
                txter.add(txt.TextPath('#' + pathid, s))

        return dwg.save_to_s3(checksum=checksum)
    except Exception as e:
        raise e
