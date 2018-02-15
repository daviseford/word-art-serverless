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
        if json_obj['simple_pre_parsed'] is not None and len(json_obj['simple_pre_parsed']) > 0:
            logger.info('Using simple_pre_parsed calculations with %s sentences' % len(json_obj['simple_pre_parsed']))
            path_str = plot_lengths(json_obj['simple_pre_parsed'])
            paths = parse_path(plot_lengths(path_str))
        else:
            logger.info('Using simple get_paths calculations')
            paths = get_paths(json_obj['text'])

        url = davis_disvg(
            paths=paths,
            node_colors=json_obj['node_colors'],
            colors=[json_obj['color']],
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
    if 'words' not in split or split['words'] is None or len(split['words']) == 0:
        return False

    return True


def get_default_arguments(event_body):
    defaults = {'text': 'sample. text.', 'node_colors': ['#4CFF57', '#007F08'],
                'color': '#2C41FF', 'split': None, 'simple_pre_parsed': None, 'split_pre_parsed': None}

    try:
        json_obj = json.loads(event_body)
        if json_obj is None:
            return defaults

        split = json_obj.get('split', None)
        if split is not None:
            split['words'] = split.get('words', ['love'])
            split['color'] = split.get('color', '#FF69B4')

        return {
            'text': json_obj.get('text', defaults['text']),
            'node_colors': json_obj.get('node_colors', defaults['node_colors']),
            'color': json_obj.get('color', defaults['color']),
            'split': split,
            'simple_pre_parsed': json_obj.get('simple_pre_parsed', defaults['simple_pre_parsed']),
            'split_pre_parsed': json_obj.get('split_pre_parsed', defaults['split_pre_parsed']),
        }
    except:
        return defaults


# TODO Add a "pre-parsed" parameter to speed this up
def endpoint(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    try:
        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Required for CORS support to work
                'Access-Control-Allow-Credentials': True,  # Required for cookies, authorization headers with HTTPS
            }
        }

        data = get_default_arguments(event['body'])
        if satisfies_split_conditions(data):
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
        logger.info(event)
        logger.info(e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Required for CORS support to work
                'Access-Control-Allow-Credentials': True,  # Required for cookies, authorization headers with HTTPS
            },
            'body': json.dumps({'err': str(e)})
        }
