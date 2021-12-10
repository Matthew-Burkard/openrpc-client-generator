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
from typing import *

from jsonrpc2pyclient.httpclient import RPCHTTPClient
from pydantic import BaseModel

from .models import *

__all__ = ("{title}{transport}Client",)


class {title}{transport}Client(RPC{transport}Client):
{methods}
    def _deserialize(self, value: Any, val_type: Union[Type, list]) -> Any:
        def _deserialize_iter(v: Any) -> Any:
            if get_origin(val_type) == list:
                return self._deserialize(v, get_args(val_type)[0])
            return val_type(**v) if issubclass(val_type, BaseModel) else v

        if isinstance(value, list):
            return [_deserialize_iter(it) for it in value]
        return _deserialize_iter(value)
""".strip()

method = """
    def {name}({args}) -> {return_type}:{doc}
        return self._deserialize(self._call('{method}', {params}), {return_type})
"""
