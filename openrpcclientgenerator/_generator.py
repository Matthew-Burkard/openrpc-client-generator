"""Client generator top-level."""
from pathlib import Path

from openrpc import OpenRPC

from openrpcclientgenerator import _python, _typescript
from openrpcclientgenerator._common import Language


def generate(openrpc: OpenRPC, language: Language, url: str, out: Path) -> None:
    """Generate an RPC client."""
    transport = "WS" if url.startswith("ws") else "HTTP"
    lang = _python if language is Language.PYTHON else _typescript
    lang.generate_client(openrpc, url, transport, out)
