try:
    import unzip_requirements
except ImportError:
    pass

import json
import logging
import traceback

from colors import DEFAULT_COLORS
from s3 import is_duplicate_checksum
from svg_simple import save_simple_xml_to_s3
from svg_split import save_split_xml_to_s3, satisfies_split_conditions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_default_arguments(event_body):
    defaults = {
        'text': 'sample. text.', 'node_colors': None,
        'color': DEFAULT_COLORS['color'], 'split': None, 'simple_pre_parsed': None,
        'split_pre_parsed': None, 'simple_path': None, 'split_path': None,
        'checksum': None, 'bg_color': DEFAULT_COLORS['bg_color']
    }

    try:
        json_obj = json.loads(event_body)
        if json_obj is None:
            return defaults

        split = json_obj.get('split', None)
        if split is not None:
            split['words'] = split.get('words', ['love'])
            split['color'] = split.get('color', DEFAULT_COLORS['split_color'])

        node_colors = json_obj.get('node_colors', defaults['node_colors'])
        if node_colors is not None:
            node_colors = [DEFAULT_COLORS['node_colors'] if c is None else c for c in node_colors]
        else:
            node_colors = None

        return {
            'text': json_obj.get('text', defaults['text']),
            'node_colors': node_colors,
            'color': json_obj.get('color', defaults['color']),
            'split': split,
            'simple_pre_parsed': json_obj.get('simple_pre_parsed', defaults['simple_pre_parsed']),
            'split_pre_parsed': json_obj.get('split_pre_parsed', defaults['split_pre_parsed']),
            'simple_path': json_obj.get('simple_path', defaults['simple_path']),
            'split_path': json_obj.get('split_path', defaults['split_path']),
            'checksum': json_obj.get('checksum', defaults['checksum']),
            'bg_color': json_obj.get('bg_color', defaults['bg_color'])
        }
    except:
        return defaults


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

        json_obj = get_default_arguments(event['body'])
        existing_url = is_duplicate_checksum(json_obj['checksum'])

        res_body = {'arguments': json_obj, 'duplicate': False}

        if existing_url is not None:
            logger.info('Duplicate detected for %s' % json_obj['checksum'])
            res_body['s3_url'] = existing_url
            res_body['duplicate'] = True
        elif satisfies_split_conditions(json_obj):
            logger.info('Creating split SVG')
            url = save_split_xml_to_s3(json_obj)
            res_body['s3_url'] = url
        else:
            url = save_simple_xml_to_s3(json_obj)
            res_body['s3_url'] = url

        response['body'] = json.dumps(res_body)
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
