# -*- coding: utf-8 -*-
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def split_into_sentences(text):
    """
    Assumes that newlines and bad chars have been removed from the text
    And all sentence-ending punctuation (like !?;:-+) has been replaced with a period
    And that the text has been lowercased
    :param text:
    :return:
    """
    try:
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences]
        return sentences
    except Exception as e:
        traceback.print_exc()
        logger.info(e)
        return []
