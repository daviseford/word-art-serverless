from svgpathtools import *
from parse_text import get_sentence_lengths
from svgpathtools import parse_path
import sys
import getopt
import os.path


def plot_lengths(array_of_ints):
    # Turn left 90 degrees each time
    behavior_ref = ['h -', 'v ', 'h ', 'v -']
    path_str = 'M50 20j'
    count = 0
    for num in array_of_ints:
        move = behavior_ref[count] + str(num)
        path_str = ' '.join([path_str, move])
        count = 0 if count == 3 else count + 1

    return path_str


def build_path_str(filepath):
    lens = get_sentence_lengths(filepath)
    path_str = plot_lengths(lens)
    return parse_path(path_str)


def make_output_path(filepath):
    return os.path.join(os.getcwd(), 'output', filepath.split('/')[-1].split('.')[0] + '.svg')


def parse_args():
    filepath = './txt/the_republic.txt' # Default
    output_opts = {
        'filename': make_output_path(filepath),
        'colors': 'b',
        'node_colors': 'bb',
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
    print '%s has %s sentences' % (filepath, len(paths))

    disvg(
        paths=[paths],
        nodes=[paths.point(0.0), paths.point(1.0)],
        node_radii=[2, 2],

        # text='Some sample text',
        # text_path=Path(Line(start=(0 + 50), end=(100 + 50))),
        # font_size=[5],
        openinbrowser=False,
        **output_opts
    )
    print 'Done! Created %s' % output_opts['filename']


if __name__ == "__main__":
    run_svg()
