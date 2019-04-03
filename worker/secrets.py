import boto3
import os

import eslog
logger = eslog.Logger(namespace='secrets')

environment = os.getenv("ENVIRONMENT")

def get_secret(name):
    if environment == 'prod':
        session = boto3.Session(region_name='eu-west-1')
        ssm = session.client('ssm')
        param = ssm.get_parameter(Name=name, WithDecryption=True)
        return  param['Parameter']['Value']
    else:
        logger.warn('Not fetching secret locally', name=name)
        return None