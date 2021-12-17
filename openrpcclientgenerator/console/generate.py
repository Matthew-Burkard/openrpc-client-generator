"""
Functions for the "generate" CLI command.

Example usage:

ocg generate \\
    --url 'http://localhost:5000/api/v1/' \\
    --lang 'python' \\
    --out './generated/' \\
    --version '1.0.0'
"""
import logging
import re
from typing import Optional

from openrpc.objects import InfoObject, OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory

log = logging.getLogger(__name__)


def generate(url: str, lang: str, out: str, version: Optional[str] = None) -> int:
    """Generate an RPC Client

    :param url: Path to OpenRPC doc or url to server with "rpc.discover"
        method.
    :param lang: Generated client language.
    :param out: Directory to save the generated code.
    :param version: Version of the client.
    :return: Process status code.
    """
    # Get OpenRPC doc.
    openrpc_doc = OpenRPCObject(
        openrpc="TODO", info=InfoObject(title="TODO", version="TODO"), methods=[]
    )
    try:
        if re.search(r"^https?://", url):
            # TODO Make rpc.discover request.
            pass
        else:
            # TODO Get doc from local file.
            pass
    except Exception as e:
        log.exception(f"{type(e).__name__}:")
        return 1

    # TODO Create out dir if it doesn't exist.
    # TODO Confirm chosen language is valid.

    # Generate client.
    try:
        cf = ClientFactory(out, openrpc_doc)
        {
            "dotnet": cf.build_dotnet_client(),
            "python": cf.build_python_client(),
            "kotlin": cf.build_kotlin_client(),
            "typescript": cf.build_typescript_client(),
        }[lang]()
    except Exception as e:
        log.exception(f"{type(e).__name__}:")
        return 1

    return 0
