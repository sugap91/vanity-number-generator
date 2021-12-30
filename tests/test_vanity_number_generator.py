import boto3
import json
import os
import sys

from moto import mock_dynamodb2


FUNC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'contacts'
)
print(FUNC_DIR)

sys.path.append(FUNC_DIR)

from index import handler  # noqa E402


class LambdaContext(object):
    def __init__(self):
        self.aws_request_id = 'abc123'
        self.invoked_function_arn = (
            'arn:aws:lambda:us-east-1:123456789012:function:'
            + 'contacts_vanity-number-generator'
        )


def create_dynamodb_table(
    table_name, keys=None, data_path=None, indexes=None
):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    if not isinstance(keys, list):
        keys = ['tenantId', 'id']
    pt = {
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
    kwargs = {
        'TableName': table_name,
        'KeySchema': [{
            'AttributeName': 'phoneNumber',
            'KeyType': 'HASH'
        }],
        'AttributeDefinitions': [{
            'AttributeName': 'phoneNumber',
            'AttributeType': 'S'
        }],
        'ProvisionedThroughput': pt
    }
    dynamodb.create_table(**kwargs)


@mock_dynamodb2
def test_vanity_generator():
    create_dynamodb_table('contacts_store')
    event = {
        'Name': 'ContactFlowEvent',
        'Details': {
            'ContactData': { 
                'CustomerEndpoint': {
                    'Address': '+1-866-266-5233', 'Type': 'TELEPHONE_NUMBER'
                }
            }
        }
    }
    output = handler(event, LambdaContext())
    assert output['result'] == 'Here are your 5 vanity numbers: 1-86MANNJADE,  1-866COOLBED,  1-866AMOKADD,  1-866COOLBEE,  1-866AMOKBEE'
