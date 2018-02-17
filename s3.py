try:
    import unzip_requirements
except ImportError:
    pass

import hashlib
import logging

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET = 'word-art-svgs'


def get_checksum(str):
    """
    Generates a sha1 checksum for a given string
    :param str:
    :return: str
    """
    hash_object = hashlib.sha1(b'%s' % str)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def get_filename(checksum):
    """
    Appends .svg to a checksum
    :param checksum:
    :return: str
    """
    return '%s.svg' % checksum


def is_duplicate_checksum(checksum):
    """
    Check if this file has been created before - if so, just return the S3 URL.
    Returns None otherwise

    :param checksum: str
    :return: str|None
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(
        Bucket=BUCKET,
        EncodingType='url',
        Prefix=checksum
    )

    if response['KeyCount'] > 0 and len(response['Contents']) > 0:
        return 'https://s3.amazonaws.com/%s/%s' % (BUCKET, response['Contents'][0]['Key'])

    return None


def upload_svg(filename, xml_string):
    """
    Uploads the SVG file to S3, and returns the URL of the object
    :param filename: str
    :param xml_string: str
    :return: str
    """
    s3 = boto3.client('s3')
    response = s3.put_object(
        ACL='public-read',
        Body=xml_string,
        Bucket=BUCKET,
        Key=filename,
        StorageClass='REDUCED_REDUNDANCY',
    )

    return 'https://s3.amazonaws.com/%s/%s' % (BUCKET, filename)


def save_svg(xml_string, checksum=None):
    """
    Saves an XML string as a unique (checksummed) file in S3
    And returns the URL of the file

    Checks for duplicates along the way using sha1 to find collisions

    :param xml_string:
    :param checksum: str|None
    :return: str
    """
    if checksum is None:
        checksum = get_checksum(xml_string)  # Get checksum of this file
        dupe_check = is_duplicate_checksum(checksum)  # Make sure it's unique
        if dupe_check is not None:
            logger.info('Duplicate detected for %s' % checksum)
            return dupe_check  # If dupe_check has a value, it's a URL to an existing (duplicate) file.

    # Usually, we've already checked for a duplicate - the above logic is just for cases
    # where we need to generate the checksum on the backend
    filename = get_filename(checksum)
    url = upload_svg(filename, xml_string)
    return url
