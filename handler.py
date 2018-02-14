try:
    import unzip_requirements
except ImportError:
    pass

import json
import logging

from svgpathtools import parse_path

from custom_svg import davis_disvg
from parse_sentences import split_into_sentences

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
        node_colors = json_obj.get('node_colors', 'bb')
        colors = json_obj.get('colors', 'b')
        url = davis_disvg(
            paths=paths,
            node_colors=node_colors,
            colors=colors,
            nodes=[paths.point(0.0), paths.point(1.0)],
            node_radii=[2, 2],
        )
        return url
    except Exception as e:
        return 'Error building xml_string: %s' % str(e)


def endpoint(event, context):
    """

    :param opts: { "text": "", "colors": "black", "node_colors": "rr" }
    :return: svg file
    """
    try:
        response = {
            'statusCode': 200,
        }

        data = event['body']
        if 'text' not in data:
            response['body'] = 'Missing text'
        else:
            url = save_xml_to_s3(json.loads(data))
            response['body'] = json.dumps({'s3_url': url})

        logger.info('Endpoint Response:')
        logger.info(response)
        return response
    except Exception as e:
        logger.info(e)
        return {'statusCode': 300, 'body': str(e)}
