import json
from datetime import datetime
import uuid
import base64
import os


# CONSTANTS
server_url = "https://zq5jg2kqvj.execute-api.us-east-1.amazonaws.com/staging"
invalidServerUrl = "https://invalid.execute-api.us-east-2.amazonaws.com/not_real"
admin_key = os.getenv('ADMIN_API_KEY')
invalid_key = "invalidApiKey123"
reg_key = os.getenv('REG_API_KEY')
no_usages_remaining_api_key = os.getenv('NO_USAGES_REMAINING_API_KEY')
origin_type = "Python Integration Tests"


invalid_order_id = "invalid_order_id"
product_id = "Atypical/MSAp/PSP-v1.0"
invalid_product_id = "not_a_real_product"

dataset_path_local = "./test_dataset"
dataset_path_git = "./tests/test_dataset"
dataset_path_local_single = "./test_dataset_single"
dataset_path_git_single = "./tests/test_dataset_single"


# HELPER FUNCTIONS
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

def is_dict(value):
    return isinstance(value, dict)

def is_valid_session_obj(conn):
    return conn and \
        is_dict(conn) and \
        is_valid_timestamp(conn.get("timestamp")) and \
        is_valid_uuid4(conn.get("connection_id")) and \
        is_valid_aes_ctr_key(conn.get('aes_key'))

def is_valid_timestamp(date_string):
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %Z")
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

def is_valid_status_obj(status_obj):
  return status_obj and is_dict(status_obj) and \
    isinstance(status_obj.get('started'), bool) and \
    isinstance(status_obj.get('finished'), bool) and \
    isinstance(status_obj.get('failed'), bool) and \
    status_obj.get('progress') and \
    isinstance(status_obj.get('progress'), int) and \
    status_obj.get('info') and \
    isinstance(status_obj.get('info'), str)


def is_valid_result_txt(result):
  return isinstance(result, str) and len(result) > 0

def is_valid_result_json(result):
    try:
        json.loads(result)
        return True
    except Exception as e:
        return False
