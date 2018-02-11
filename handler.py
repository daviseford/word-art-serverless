try:
    import unzip_requirements
except ImportError:
    pass

from parse_sentences import split_into_sentences
from svgpathtools import parse_path
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


def build_path_str(text):
    lens = get_sentence_lengths(text)
    path_str = plot_lengths(lens)
    return parse_path(path_str)


def endpoint(event, context):
    """

    :param opts: { "text": "", "color": "black" }
    :return: svg file
    """
    try:
        response = {
            "statusCode": 200,
            # "body": json.loads(event),
        }

        data = event['body']
        if 'text' not in data:
            response["body"] = 'Missing text'
        else:
            paths = build_path_str(json.loads(data)['text'])
            logger.info('paths')
            logger.info(paths)
            # TODO CONVERT PATHS TO STRING OR SVG OR SOMETHING, BUT THIS IS WORKING!!
            response['body'] = paths

        logger.info('response')
        logger.info(response)
        return response
    except Exception as e:
        traceback.print_exc()
        return {'statusCode': 300, 'body': str(e)}


