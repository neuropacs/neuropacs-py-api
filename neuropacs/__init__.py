# __init__.py
from .sdk import Neuropacs

PACKAGE_VERSION = "1.3.6"

def init(api_key, server_url):
    return Neuropacs(api_key=api_key, server_url=server_url)


