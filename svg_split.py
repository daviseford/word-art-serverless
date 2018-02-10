from svgpathtools import *
from parse_text_split import get_sentence_lengths
from svgpathtools import parse_path, Line
import sys
import getopt
import os.path


def strip_non_alpha(word):
    exclusion_list = ["(", ")"]
    return ''.join(x for x in word if x not in exclusion_list)


def fix_coordinate(str):
    if len([x for x in str if x in ['(', ')']]) == 0:
        return '%s+0' % str
    else:
        return str


def plot_lengths(a):
    """

    :param a: [{'color':'','length':5}]
    :return: [{'color': 'red', 'path': Path()}]
    """
    # Turn left 90 degrees each time
    behavior_ref = ['h -', 'v ', 'h ', 'v -']
    path_store = []
    path_str = 'M50 20j'
    count = 0
    color = a[0].get('color', 'black')
    for obj in a:

        if obj['color'] != color:
            print 'Changed colors from %s to %s' % (color, obj['color'])
            last_point = fix_coordinate(str(parse_path(path_str).point(1.0)))
            new_path_start = 'M%s' % strip_non_alpha(last_point)
            res = {'color': color, 'path': parse_path(path_str)}
            path_store.append(res)  # Add the Path to the line_store
            path_str = new_path_start  # Start the new path
            color = obj['color']  # With the new color

        move = behavior_ref[count] + str(obj['length'])
        path_str = ' '.join([path_str, move])
        count = 0 if count == 3 else count + 1

    # Add the last entry
    path_store.append({'color': color, 'path': parse_path(path_str)})
    return path_store


def build_path_str(filepath):
    """

    :param filepath:
    :return: [{'color':'red','path':Path()}]
    """
    lens = get_sentence_lengths(filepath)
    arr_of_path_objs = plot_lengths(lens)

    return arr_of_path_objs


def make_output_path(filepath):
    return os.path.join(os.getcwd(), 'output', filepath.split('/')[-1].split('.')[0] + '.svg')


def parse_args():
    filepath = './txt/lyme_savvy.txt'  # Default
    output_opts = {
        'filename': make_output_path(filepath),
        'node_colors': ['#4CFF57', '#007F08'],  # light green, dark green
    }
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:c:", ["file=", "color="])
    except getopt.GetoptError:
        print 'python svg.py -f <inputfile> -c <color "#fff" or "b">'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'python svg.py -f <inputfile> -c <color "#fff">'
            sys.exit()
        elif opt in ("-f", "--file"):
            filepath = arg
            if os.path.isfile(filepath):
                output_opts['filename'] = make_output_path(filepath)
            else:
                print 'Invalid filepath %s' % filepath
                sys.exit()
        elif opt in ("-c", "--color"):
            output_opts['colors'] = [arg]
            output_opts['node_colors'] = [arg, arg]

    return filepath, output_opts


def run_svg():
    filepath, output_opts = parse_args()
    paths = build_path_str(filepath)
    print '%s has %s different paths' % (filepath, len(paths))
    # print paths

    disvg(
        paths=[x['path'] for x in paths],
        colors=[x['color'] for x in paths],
        nodes=[paths[0]['path'].point(0.0), paths[-1]['path'].point(1.0)],
        node_radii=[3, 3],
        openinbrowser=False,
        **output_opts
    )
    print 'Done! Created %s' % output_opts['filename']


if __name__ == "__main__":
    run_svg()
