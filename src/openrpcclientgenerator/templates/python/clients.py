rpc_http_client = """
from typing import Optional, Union

from requests import Session

from jsonrpc2pyclient.rpcclient import RPCClient


class RPCHTTPClient(RPCClient):
    def __init__(self, url: str, headers: Optional[dict] = None) -> None:
        self.session = Session()
        headers = headers or {}
        headers['contentType'] = 'application/json'
        self.session.headers = headers
        self.url = url

    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return self.session.post(url=self.url, data=request_json).content
"""
