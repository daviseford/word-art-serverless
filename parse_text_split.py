import nltk  # http://www.nltk.org/
from nltk.tokenize import TweetTokenizer
import string
import io


def read_file(path):
    try:
        f = io.open(path, mode="r", encoding="utf-8")  # Using io allows us to specify the encoding
        return f.read()
    except Exception as e:
        raise e


def get_sentences(input_text):
    """

    :param input_text:
    :return: { 'color' : str , 'length': int }
    """
    try:
        tokenizer_words = TweetTokenizer()
        tokens_sentences = [tokenizer_words.tokenize(x) for x in nltk.sent_tokenize(input_text)]
        sentence_words = [filter_alpha(x) for x in tokens_sentences]

        bg = 'black'
        primary = 'red'
        secondary = 'white'
        keywords = [
            # {'k': 'DOCTORSPLIT', 'c': '#02799a'},  # blue
            # {'k': 'SHARONSPLIT', 'c': '#E70F52'},  # pink
            #
            # {'k': 'DOCTORHOCKSTRASPLIT', 'c': 'black'},
            # {'k': 'JEFFSPLIT', 'c': '#C7795F'},
            # {'k': 'KATHYSPLIT', 'c': 'black'},
            # {'k': 'PARRISHSPLIT', 'c': 'black'},
            # {'k': 'SECTIONSPLIT', 'c': 'grey'},
            # {'k': 'SHIRLEYSPLIT', 'c': 'black'},

            {'k': 'quality', 'c': primary},

        ]
        default_color = secondary


        store = []
        for arr_of_words in sentence_words:
            c = default_color
            zz = [x.lower() for x in arr_of_words]
            for x in keywords:
                if x['k'].lower() in zz:
                    c = x['c']

            store.append({'color': c, 'length': len(arr_of_words)})

        return store
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


def get_sentence_lengths(path_to_src_text):
    """

    :param path_to_src_text:
    :return: [{ 'color' : str , 'length': int }]
    """
    input_text = read_file(path_to_src_text)
    res = get_sentences(input_text)
    return res

# print get_sentence_lengths('./txt/bible.txt')
