try:
    import unzip_requirements
except ImportError:
    pass

import json
import logging
import traceback

from svgpathtools import parse_path

from custom_svg import davis_disvg
from parse_sentences import split_into_sentences
from svg_split import save_split_xml_to_s3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def filter_length(list_of_sentence_lists):
    return [len(x) for x in list_of_sentence_lists]


def get_sentence_lengths(input_text):
    """

    :param input_text: str
    :return:
    """
    sentences = split_into_sentences(input_text)
    return filter_length(sentences)


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


def get_paths(text):
    """

    :param text:
    :return:
    """
    sentence_lengths = get_sentence_lengths(text)
    path_str = plot_lengths(sentence_lengths)
    return parse_path(path_str)


def save_xml_to_s3(json_obj):
    """

    :param json_obj:
    :return: str
    """
    try:
        paths = get_paths(json_obj['text'])
        node_colors = json_obj.get('node_colors', ['#FF4C4C', '#CC0000'])
        colors = json_obj.get('color', '#2C41FF')
        url = davis_disvg(
            paths=paths,
            node_colors=node_colors,
            colors=[colors],
            nodes=[paths.point(0.0), paths.point(1.0)],
            node_radii=[2, 2],
        )
        return url
    except Exception as e:
        traceback.print_exc()
        return 'Error building xml_string: %s' % str(e)


def satisfies_split_conditions(json_obj):
    """

    :param json_obj:
    :return: bool
    """
    if 'split' not in json_obj or json_obj.get('split', None) is None:
        return False
    split = json_obj['split']
    if 'words' not in split or 'color' not in split or '#' not in json_obj['color']:
        return False
    if len(split['words']) == 0 or '#' not in split['color']:
        return False

    return True


def endpoint(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    try:
        response = {
            'statusCode': 200,
        }

        data = json.loads(event['body'])

        if 'text' not in data:
            logger.info('Missing text')
            response['body'] = 'Missing text'
        elif satisfies_split_conditions(data):
            logger.info('Creating split SVG')
            url = save_split_xml_to_s3(data)
            response['body'] = json.dumps({'s3_url': url})
        else:
            url = save_xml_to_s3(data)
            response['body'] = json.dumps({'s3_url': url})

        logger.info('Endpoint Response:')
        logger.info(response)
        return response
    except Exception as e:
        logger.info('Incoming data for this error:')
        logger.info(json.loads(event['body']))
        logger.info(e)
        return {'statusCode': 300, 'body': str(e)}
