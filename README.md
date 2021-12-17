<div align=center>
<!-- Title: -->
  <h1>OpenRPC Client Generator</h1>
<!-- Labels: -->
  <!-- First row: -->
  <img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg"
   height="20"
   alt="License: AGPL v3">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"
   height="20"
   alt="Code style: black">
  <a href="https://gitlab.com/mburkard/openrpc-client-generator/-/blob/main/CONTRIBUTING.md">
    <img src="https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=2267a0"
     height="20"
     alt="Contributions Welcome">
  </a>
  <h3>Generate clients for various languages from OpenRPC documents</h3>
</div>

This library provides a `ClientFactory` class that can be used to
generate clients.

Current supported languages:
- Python
- TypeScript
- C#

For each client two files will be generated, a models file with code for
which will have a class for each schema, and a client file which have
all the methods. Then the files will be built into a distributable
package.

## Example Usage

```python
import json

from openrpc.objects import OpenRPCObject
from openrpcclientgenerator.client_factory import ClientFactory

openrpc_doc_obj = OpenRPCObject(**json.loads(openrpc_doc_json))
client_dir = "./dist/generated/"

cf = ClientFactory(out_dir=client_dir, rpc=openrpc_doc_obj)
cf.build_python_client()
cf.build_dotnet_client()
cf.build_typescript_client()
```
