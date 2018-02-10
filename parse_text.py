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
    try:
        tokenizer_words = TweetTokenizer()
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


def get_sentence_lengths(path_to_src_text):
    input_text = read_file(path_to_src_text)
    sentences = get_sentences(input_text)
    return filter_length(sentences)

# print get_sentence_lengths('./txt/bible.txt')
