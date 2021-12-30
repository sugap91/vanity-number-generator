from collections import Mapping
from collections import OrderedDict
from datetime import datetime
import dateutil
import gzip
from io import BytesIO
import json
import logging
import os
import sys
import time

from boto3.dynamodb.types import Binary
from boto3.dynamodb.types import Decimal


is_dictionary_trie_populated = False
DICTIONARY_TRIE = None


def info(msg, extra=None):
    if extra is not None:
        logging.info(msg, extra)
    else:
        logging.info(msg)


def error(msg, extra=None):
    if extra is not None:
        logging.error(msg, extra)
    else:
        logging.error(msg)


def fatal(msg, extra=None):
    if extra is not None:
        logging.critical(msg, extra)
    else:
        logging.critical(msg)
    sys.exit(1)


def get_envvar(var, default):
    """Get default environment variable

    Args:
        var (str): environment variable name
        default (any): default value

    Returns:
        environment variable value or default

    """
    val = os.environ.get(var)
    # convert value to int
    if isinstance(default, int) and val is not None:
        try:
            val = int(val)
        except Exception:
            val = default
    if val is None:
        val = default
    return val


def debug(msg, level=1):
    if os.environ.get('DEBUG', 'FALSE') != 'TRUE':
        return
    debug_level = get_envvar('DEBUG_LEVEL', 1)
    if debug_level >= level:
        print('DEBUG%s: %s' % (level, msg))


def add_utc_tz(x):
    return x.replace(tzinfo=dateutil.tz.gettz("UTC"))


def now_dt():
    """Returns UTC datetime

    Returns:
        datetime: datetime

    """
    return add_utc_tz(datetime.utcnow())


def timestamp(obj=None, format=None):
    """Returns ISO timestamp in format %Y-%m-%dT%H:%M:%S.%fZ

    Current time used if obj not specified

    Args:
        obj (datetime or int, optional): datetime or epoch seconds
        format (str, optional): format of timestamp

    Returns:
        str: timestamp

    """
    if format is None:
        format = '%Y-%m-%dT%H:%M:%S.%fZ'
    if obj is None:
        obj = now_dt()
    ts = None
    if isinstance(obj, datetime):
        ts = obj.strftime(format)
        if ts.endswith('Z'):
            ts = ts[:-4] + 'Z'
    else:
        ts = time.strftime(format, time.gmtime(obj))
        ts = ts.replace('.fZ', '.000Z')
    return ts


def gunzip_data(gz_body):
    """Gzip uncompresses string

    Args:
        gz_body: binary gzipped value

    Returns:
        str: uncompressed string

    """
    gzf = gz_body if isinstance(gz_body, BytesIO) else BytesIO(gz_body)
    txt = gzip.GzipFile(fileobj=gzf).read()
    return txt


# http://stackoverflow.com/questions/11875770/
# how-to-overcome-datetime-datetime-not-json-serializable-in-python
# see https://github.com/Alonreznik/dynamodb-json/blob/
# master/dynamodb_json/json_util.py
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        if obj % 1 > 0:
            return float(obj)
        else:
            return int(obj)
        return float(obj)
    if isinstance(obj, Binary):
        return json.loads(gunzip_data(obj.value))
    if isinstance(obj, set):
        return list(obj)
    raise TypeError('type not serializable')
