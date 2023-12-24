# __init__.py
from .sdk import Neuropacs

PACKAGE_VERSION = "1.3.7"

def init(api_key, server_url):
    return Neuropacs(server_url=server_url, api_key=api_key)


