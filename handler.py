try:
    import unzip_requirements
except ImportError:
    pass

from parse_sentences import split_into_sentences
from svgpathtools import parse_path
from custom_svg import davis_disvg
import json
import traceback
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def filter_length(list_of_sentence_lists):
    return [len(x) for x in list_of_sentence_lists]


def get_sentence_lengths(input_text):
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


def build_xml_str(json_obj):
    lens = get_sentence_lengths(json_obj.get('text', 'Sample. Text.'))
    path_str = plot_lengths(lens)
    paths = parse_path(path_str)
    return davis_disvg(
        paths=paths,
        node_colors=json_obj.get('node_colors', 'bb'),
        colors=json_obj.get('colors', 'b'),
        nodes=[paths.point(0.0), paths.point(1.0)],
        node_radii=[2, 2],
    )


def endpoint(event, context):
    """

    :param opts: { "text": "", "colors": "black", "node_colors": "rr" }
    :return: svg file
    """
    try:
        response = {
            "statusCode": 200,
        }

        data = event['body']
        if 'text' not in data:
            response["body"] = 'Missing text'
        else:
            xml_string = build_xml_str(json.loads(data))
            response['body'] = json.dumps({'xml': xml_string})

        logger.info('response')
        logger.info(response)
        return response
    except Exception as e:
        logger.info(e)
        traceback.print_exc()
        return {'statusCode': 300, 'body': str(e)}
