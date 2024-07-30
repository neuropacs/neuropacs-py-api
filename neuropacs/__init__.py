# __init__.py
from .sdk import Neuropacs

PACKAGE_VERSION = "1.7.9"

def init(server_url, api_key, origin_type="API"):
    return Neuropacs(server_url=server_url, api_key=api_key, origin_type=origin_type)


