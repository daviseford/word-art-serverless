try:
    import unzip_requirements
except ImportError:
    pass

from svgpathtools import parse_path
import json
import nltk  # http://www.nltk.org/
import string


def get_sentences(input_text):
    try:
        tokenizer_words = nltk.tokenize.TweetTokenizer()
        tokens_sentences = [tokenizer_words.tokenize(x) for x in nltk.sent_tokenize(input_text)]
        sentence_words = [filter_alpha(x) for x in tokens_sentences]
        return sentence_words
    except Exception as e:
        raise e


def filter_alpha(a_list):
    stripped = [strip_non_alpha(x) for x in a_list]
    return [x.lower() for x in stripped if x.isalpha() and x is not None]


def filter_length(list_of_sentence_lists):
    return [len(x) for x in list_of_sentence_lists]


def strip_non_alpha(word):
    exclusion_list = set(string.punctuation)
    return ''.join(x for x in word if x not in exclusion_list)


def get_sentence_lengths(input_text):
    sentences = get_sentences(input_text)
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

    response = {
        "statusCode": 200,
        "body": json.loads(event),
        # "body": 'asdasd'
    }
    # return response

    data = json.loads(event['body'])
    if 'text' not in data:
        response["body"] = 'FUCK'
        return response

    output_opts = {
        'filename': 'test1.svg',
        'colors': 'red',
        'node_colors': 'bb',
    }
    paths = build_path_str(data['text'])

    # disvg(
    #     paths=[paths],
    #     nodes=[paths.point(0.0), paths.point(1.0)],
    #     node_radii=[2, 2],
    #
    #     # text='Some sample text',
    #     # text_path=Path(Line(start=(0 + 50), end=(100 + 50))),
    #     # font_size=[5],
    #     openinbrowser=False,
    #     **output_opts
    # )

    # response['body'] = 'Done! Created %s' % output_opts['filename']
    response['body'] = {'event': json.loads(event), 'svg_string': paths}

    return response
