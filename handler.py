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
    try:
        response = {
            "statusCode": 200,
            # "body": json.loads(event),
        }

        data = event['body']
        if 'text' not in data:
            response["body"] = 'FUCK'
        else:
            paths = build_path_str(data['text'])
            response['body'] = json.dumps({'event': event, 'svg_string': paths})

        return response
    except Exception as e:
        return {'statusCode': '300', 'body': json.dumps({'error': e, 'event': event})}
