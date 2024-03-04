# __init__.py
from .sdk import Neuropacs

PACKAGE_VERSION = "1.5.2"

def init(server_url, socket_url, api_key):
    return Neuropacs(server_url=server_url, socket_url=socket_url, api_key=api_key)


