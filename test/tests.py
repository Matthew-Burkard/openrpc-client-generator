import json
import os
from pathlib import Path

from openrpc.objects import OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory

pwd = os.getcwd()
openrpc_doc = OpenRPCObject(**json.loads(Path(f"{pwd}/openrpc.json").read_text()))
cf = ClientFactory(f"{pwd}/../dist/generated", openrpc_doc)

cf.build_c_sharp_client()
cf.build_python_client()
cf.build_typescript_client()
