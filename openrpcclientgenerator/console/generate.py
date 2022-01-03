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

from openrpcclientgenerator.client_factory import ClientFactory, Language
from openrpcclientgenerator.console import discover

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
    try:
        if re.search(r"^https?://", url):
            openrpc_doc = discover.discover(url)
        else:
            openrpc_doc = discover.from_file(url)
    except Exception as e:
        log.exception(f"{type(e).__name__}:")
        return 1

    try:
        language = Language(lang)
    except ValueError:
        languages = ", ".join(it.value for it in Language)
        log.exception(f"{lang} is not a valid language, must be one of: {languages}")
        return 1

    # Generate client.
    try:
        cf = ClientFactory(out, openrpc_doc)
        cf.generate_client(language)
    except Exception as e:
        log.exception(f"{type(e).__name__}:")
        return 1

    return 0
