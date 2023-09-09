"""Client generator top-level."""
from pathlib import Path

from openrpc import OpenRPC

from openrpcclientgenerator import _python, _typescript
from openrpcclientgenerator._common import Language, Transport


def generate(
    openrpc: OpenRPC, language: Language, transport: Transport, url: str, out: Path
) -> None:
    """Generate an RPC client."""
    lang = _python if language is Language.PYTHON else _typescript
    lang.generate_client(openrpc, url, transport.value, out)
