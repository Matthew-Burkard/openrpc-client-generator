"""Methods to get an OpenRPC object from different sources."""
import json
from pathlib import Path

import httpx
from openrpc.objects import OpenRPCObject


def discover(url: str) -> OpenRPCObject:
    """Get an OpenRPC doc from the "rpc.discover" method of server."""
    req = {"id": 1, "method": "rpc.discover", "jsonrpc": "2.0"}
    res = httpx.post(url, json=req)
    return OpenRPCObject(**res.json()["result"])


def from_file(path: str) -> OpenRPCObject:
    """Get an OpenRPC doc from a file."""
    return OpenRPCObject(**json.loads(Path(path).read_text()))
