try:
    import unzip_requirements
except ImportError:
    pass

import logging
import string
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from svgpathtools import parse_path

from custom_svg import davis_disvg
from parse_sentences import split_into_sentences


def get_sentences(input_text, split_dict, primary_color):
    """

    :param input_text: str
    :param primary_color: str
    :param split_dict: { words: [str,str], color: str }
    :return: { 'color' : str , 'length': int }
    """
    try:
        array_of_sentences = split_into_sentences(input_text)
        default_color = primary_color
        store = []
        for array_of_words in array_of_sentences:
            segment_color = default_color
            for highlight_word in split_dict['words']:
                if highlight_word.lower() in array_of_words:
                    segment_color = split_dict['color']

            store.append({'color': segment_color, 'length': len(array_of_words)})

        return store
    except Exception as e:
        traceback.print_exc()
        logger.info(e)
        raise e


def filter_alpha(a_list):
    stripped = [strip_non_alpha(x) for x in a_list]
    return [x.lower() for x in stripped if x.isalpha() and x is not None]


def filter_length(list_of_sentence_lists):
    return [len(x) for x in list_of_sentence_lists]


def strip_non_alpha(word):
    exclusion_list = set(string.punctuation)
    return ''.join(x for x in word if x not in exclusion_list)


def strip_parens(word):
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
            # print 'Changed colors from %s to %s' % (color, obj['color'])
            last_point = fix_coordinate(str(parse_path(path_str).point(1.0)))
            new_path_start = 'M%s' % strip_parens(last_point)
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


def build_path_str(json_obj):
    """

    :param input_text: str
    :return: [{'color':'red','path':Path()}]
    """
    try:
        sentence_lengths = get_sentences(json_obj['text'], json_obj['split'], json_obj['color'])
        return plot_lengths(sentence_lengths)
    except Exception as e:
        logger.info(e)
        traceback.print_exc()
        return []


def save_split_xml_to_s3(json_obj):
    """

    :param json_obj:
    :return:
    """
    try:
        if json_obj['split_pre_parsed'] is not None and len(json_obj['split_pre_parsed']) > 0:
            logger.info('Using split_pre_parsed calculations with %s sentences' % len(json_obj['split_pre_parsed']))
            paths = plot_lengths(json_obj['split_pre_parsed'])
        else:
            logger.info('Using split get_paths calculations')
            paths = build_path_str(json_obj)

        node_colors = json_obj['node_colors']

        url = davis_disvg(
            paths=[x['path'] for x in paths],
            colors=[x['color'] for x in paths],
            nodes=[paths[0]['path'].point(0.0), paths[-1]['path'].point(1.0)],
            node_colors=node_colors,
            node_radii=[2, 2],
        )

        return url
    except Exception as e:
        traceback.print_exc()
        return 'Error building xml_string: %s' % str(e)
