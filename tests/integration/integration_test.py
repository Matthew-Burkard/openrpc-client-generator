"""Generate client, build it, use it on test server."""
import os
import subprocess
from pathlib import Path

import caseswitcher as cs
from openrpc import OpenRPCObject

from integration.test_server import rpc
from openrpcclientgenerator.client_factory import ClientFactory, Language
from openrpcclientgenerator.generators.transports import Transport

out_dir = Path("./out")
rpc_doc = OpenRPCObject(**rpc.discover())
cf = ClientFactory(rpc_doc, out_dir)


def python_ws() -> None:
    """Build Python websocket client."""
    cf.generate_client(Language.PYTHON, Transport.WS, remove_existing=True)
    pkg_name = f"{cs.to_snake(rpc_doc.info.title)}_client"
    client_path = out_dir / "python" / pkg_name
    cwd = Path.cwd()
    os.chdir(client_path)
    subprocess.run(["poetry", "build"])
    os.chdir(cwd)
    # tarball_path = f"{client_path}/dist/{pkg_name}-{rpc.info.version}.tar.gz"


if __name__ == "__main__":
    python_ws()
