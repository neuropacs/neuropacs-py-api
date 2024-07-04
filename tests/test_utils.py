import json
from datetime import datetime
import base64
import uuid

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

def is_dict(value):
    return isinstance(value, dict)

def is_valid_timestamp(date_string):
    try:
        naive_datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return False
    return True

def is_valid_uuid4(value):
    try:
        val = uuid.UUID(value, version=4)
    except ValueError:
        return False
    return True

def is_valid_aes_ctr_key(key):
    try:
        decoded_key = base64.b64decode(key, validate=True)
    except (ValueError, base64.binascii.Error):
        return False
    return True

