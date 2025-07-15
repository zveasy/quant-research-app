import os
import boto3
import requests

ssm = boto3.client('ssm')
ecs = boto3.client('ecs')

PAGERDUTY_URL = os.getenv('PAGERDUTY_URL')
QUEUE_URL = os.getenv('ROLLBACK_QUEUE_URL')
PARAM_NAME = os.getenv('MODEL_SHA_PARAM', '/model/sha')
CLUSTER = os.getenv('ECS_CLUSTER')
SERVICE = os.getenv('ECS_SERVICE')


def handle_message(msg):
    if msg.get('Body') != 'ROLLBACK':
        return
    last_good = ssm.get_parameter(Name=PARAM_NAME, WithDecryption=False)["Parameter"]["Value"]
    ssm.put_parameter(Name=PARAM_NAME, Value=last_good, Overwrite=True)
    ecs.update_service(cluster=CLUSTER, service=SERVICE, forceNewDeployment=True)
    if PAGERDUTY_URL:
        requests.post(PAGERDUTY_URL, json={'event_action': 'trigger', 'payload': {'summary': 'Model rollback', 'severity': 'critical'}})


def lambda_handler(event, context):
    for record in event.get('Records', []):
        handle_message(record)
