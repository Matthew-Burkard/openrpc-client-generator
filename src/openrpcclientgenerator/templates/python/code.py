# Models
model_file = """
from typing import Optional

from pydantic import BaseModel

{classes}
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
from .models import *


class {title}Client(RPC{transport}Client):
{methods}
""".strip()

method = """
    def {name}({args}) -> {return_type}:
        {doc}
        result = self._call('{method}', [{params}])
        {deserialize}
        return result
"""
deserialize_class = """
        if issubclass({return_type}, BaseModel):
            return {return_type}(**result)
""".strip()
deserialize_list = """
        ret_val = []
        for it in result:
            if issubclass({type}, BaseModel):
                ret_val.append({type}(**it))
            else:
                ret_val.append(it)
        result = ret_val
""".strip()
