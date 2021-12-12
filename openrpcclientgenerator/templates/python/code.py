"""Python code templates."""

# Models
model_file = """
from __future__ import annotations

from typing import *

from pydantic import BaseModel

__all__ = ({all},)

{classes}
{update_refs}
""".strip()

data_class = """
class {name}(BaseModel):
    {doc}
    {fields}
"""
field = "{name}: {type}{default}"

# Methods
client_file = """
\"""
Provides synchronous and asynchronous clients for {title} server.
\"""
from typing import *

from jsonrpc2pyclient.httpclient import AsyncRPC{transport}Client, RPC{transport}Client
from pydantic import BaseModel

from .models import *

__all__ = ("Async{title}{transport}Client", "{title}{transport}Client")


class Async{title}Client(AsyncRPC{transport}Client):
    \"""Generated async client for {title} server.\"""
{async_methods}


class {title}Client(RPC{transport}Client):
    \"""Generated client for {title} server.\"""
{methods}


def _deserialize(value: Any, val_type: Union[Type, list]) -> Any:
    def _deserialize_iter(v: Any) -> Any:
        if get_origin(val_type) == list:
            return _deserialize(v, get_args(val_type)[0])
        return val_type(**v) if issubclass(val_type, BaseModel) else v

    if isinstance(value, list):
        return [_deserialize_iter(it) for it in value]
    return _deserialize_iter(value)
""".strip()

async_method = """
    async def {name}({args}) -> {return_type}:{doc}
        return _deserialize(await self.call('{method}', {params}), {return_type})
"""

method = """
    def {name}({args}) -> {return_type}:{doc}
        return _deserialize(self.call('{method}', {params}), {return_type})
"""
