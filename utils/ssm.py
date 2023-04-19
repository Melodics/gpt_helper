import json
import os
import boto3
import logging
import traceback


logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_ssm_parameter(parameter_name):
    log = logging.getLogger('ssm')
    value = ''
    response = None
    try:
        ssm_client = boto3.client('ssm', region_name='us-east-1')
        log.info(ssm_client)

        response = ssm_client.get_parameter(
            Name=parameter_name, WithDecryption=True)

        value = response['Parameter']['Value']
    except Exception as e:
        log.error('Failed to retrieve parameter {}. Result was {}. Exception was {}'.format(
            parameter_name, response, e))
        log.error(traceback.format_exc())
        value = os.getenv(parameter_name, value)
    return value


def get_secrets_manager_parameter(parameter_name):
    log = logging.getLogger('secretsmanager')
    value = ''
    response = None
    try:
        secrets_manager_client = boto3.client('secretsmanager')
        response = secrets_manager_client.get_secret_value(
            SecretId='slack/gpt-helper-api-keys'
        )
        json_response = json.loads(response['SecretString'])
    except Exception as e:
        log.error('Failed to retrieve parameter {}. Result was {}. Exception was {}'.format(
            parameter_name, response, e))
        log.error(traceback.format_exc())
        value = os.getenv(parameter_name, value)
    return json_response[parameter_name]