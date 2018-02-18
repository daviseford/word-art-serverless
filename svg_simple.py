try:
    import unzip_requirements
except ImportError:
    pass

import logging
import traceback

from svgpathtools import parse_path

from custom_svg import davis_disvg
from parse_sentences import split_into_sentence_lengths

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def filter_length(list_of_sentence_lists):
    return [len(x) for x in list_of_sentence_lists]


def get_sentence_lengths(input_text):
    sentence_lengths = split_into_sentence_lengths(input_text)
    return sentence_lengths


def plot_lengths(array_of_ints):
    # Turn left 90 degrees each time
    behavior_ref = ['h -', 'v ', 'h ', 'v -']
    path_str = 'M50 20j'
    count = 0
    for num in array_of_ints:
        move = '%s%s' % (behavior_ref[count], num)
        path_str = ' '.join([path_str, move])
        count = 0 if count == 3 else count + 1

    return path_str


def get_simple_preparsed_paths(simple_path):
    return parse_path(simple_path)


def get_simple_paths(text):
    """

    :param text:
    :return:
    """
    sentence_lengths = get_sentence_lengths(text)
    path_str = plot_lengths(sentence_lengths)
    return parse_path(path_str)


def save_simple_xml_to_s3(json_obj):
    """

    :param json_obj:
    :return: str
    """
    try:
        if json_obj['simple_path'] is not None and len(json_obj['simple_path']) > 0:
            logger.info('Using simple_path parameter')
            paths = get_simple_preparsed_paths(json_obj['simple_path'])
        else:
            logger.info('Using simple get_paths calculations')
            paths = get_simple_paths(json_obj['text'])

        if json_obj['node_colors'] is not None:
            node_opts = {'node_colors': json_obj['node_colors'], 'node_radii': [1, 1]}
        else:
            node_opts = {'node_colors': None, 'node_radii': [0, 0]}

        url = davis_disvg(
            paths=paths,
            colors=[json_obj['color']],
            nodes=[paths.point(0.0), paths.point(1.0)],
            checksum=json_obj['checksum'],
            bg_color=json_obj['bg_color'],
            **node_opts
        )
        return url
    except Exception as e:
        traceback.print_exc()
        return 'Error building xml_string: %s' % str(e)
