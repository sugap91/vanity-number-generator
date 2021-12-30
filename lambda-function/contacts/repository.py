from collections import Mapping
import json
import os

import boto3
from botocore.exceptions import ClientError

import common
from exceptions import ItemNotFoundException
from exceptions import RepositoryException


class Repository(object):
    entity = None
    repository = None

    def __init__(self, entity, hk):
        """Persistence store for vanity numbers

        Args:
            entity (str): dynamodb table
            hk (str): hash key

        """
        self.entity = entity
        self.hk_attr = hk
        self.repository = 'dynamodb'

    def get(self, hk):
        """Get respository item

        Args:
            hk (str): hash key

        Returns:
            dict: repository item

        Raises:
            ItemNotFoundException: when repository item doesnt exist

        """
        return self._call('get', hk)

    def exists(self, hk, must_exist=False):
        """Return True if respository item exists otherwise False

        Args:
            hk (str): hash key / tenant ID

        Returns:
            boolean: True or False

        """
        try:
            item = self._call('get', hk)
        except ItemNotFoundException:
            if must_exist is True:
                raise ItemNotFoundException(
                    '%s not found' % self.entity,
                    '%s %s not found' % (self.entity, hk)
                )
            return False
        except Exception as e:
            raise RepositoryException(
                'unable to determine if %s exists' % self.entity,
                e
            )
        return item

    def write(self, hk, vals=None, update=False):
        """Write respository item

        Args:
            hk (str): hash key / tenant ID
            vals (dict): dictionary of values to write
            update (bool): update (default)

        """
        if not isinstance(vals, Mapping) or len(vals) == 0:
            raise RepositoryException(
                'unable to write to repository',
                'vals must be non empty dict'
            )
        if 'lastModified' not in vals:
            vals['lastModified'] = common.timestamp()
        return self._call('write', hk, vals=vals, update=update)

    def _call(self, operation, hk, **kwargs):
        suffix = 'item'
        method_name = '_%s_%s_%s' % (
            operation, self.repository, suffix
        )
        common.debug(
            'repository._call() %s(%s, %s)' % (
                method_name, hk, kwargs
            ), 2
        )
        method = getattr(self, method_name)
        return method(hk, **kwargs)

    def _get_dynamodb_table(self):
        kwargs = {
            'region_name': os.environ.get('AWS_REGION', 'us-east-1')
        }
        return boto3.resource('dynamodb', **kwargs).Table(self.entity)

    def _get_dynamodb_key(self, hk):
        key = {}
        key[self.hk_attr] = hk
        return key

    def _get_dynamodb_item(self, hk):
        title = '%s not found' % self.entity
        detail = '%s not found' % (self.entity)
        dbgmsg = 'unable to get dynamodb item %s [%s]' % (
            self.entity, hk
        )
        response = None
        try:
            response = self._get_dynamodb_table().get_item(
                Key=self._get_dynamodb_key(hk)
            )
        except ClientError as e:
            code = e.response['Error']['Code']
            raise RepositoryException(
                title,
                '%s: %s' % (detail, code)
            )
        except Exception as e:
            raise RepositoryException(
                '%s: %s' % (detail, e),
                e
            )
        if 'Item' not in response:
            common.error('ERROR: %s' % dbgmsg)
            raise ItemNotFoundException(
                title,
                detail
            )
        try:
            item = json.loads(json.dumps(
                response['Item'], default=common.json_serial
            ))
            return item
        except Exception as e:
            raise RepositoryException(
                title,
                '%s: %s' % (detail, e)
            )

    def _write_dynamodb_item(self, hk, vals, update=False):
        title = 'unable to %s %s' % (
            'update' if update is True else 'create',
            self.entity
        )
        try:
            table = self._get_dynamodb_table()
            key = self._get_dynamodb_key(hk)
            vals.pop(self.hk_attr, None)
            if update is True:
                kwargs = {
                    'Key': key,
                    'ReturnValues': 'ALL_NEW'
                }
                exp = []
                _vals = {}
                aliases = {}
                for k, v in sorted(vals.items()):
                    if isinstance(v, str) and v == '':
                        v = None
                    aliases['#%s' % k] = k
                    exp.append('#%s = :%s' % (k, k))
                    _vals[':%s' % k] = v
                if len(_vals):
                    kwargs['ExpressionAttributeValues'] = _vals
                    kwargs['UpdateExpression'] = 'set %s' % ', '.join(exp)
                if len(aliases):
                    kwargs['ExpressionAttributeNames'] = aliases
                    print(kwargs)
                    response = table.update_item(**kwargs)
                    vals.update(response.get('Attributes'))
            else:
                vals.update(key)
                print(vals)
                table.put_item(Item=vals)
            return vals
        except Exception as e:
            raise RepositoryException(
                title,
                'unable to write dynamodb item %s [%s]: %s' % (
                    self.entity, hk, e
                )
            )
