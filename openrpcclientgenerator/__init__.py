"""Generate Open-RPC clients.

Current supported languages:
 - Python
 - TypeScript
"""

__all__ = ("generate", "Language")

from openrpcclientgenerator._common import Language
from openrpcclientgenerator._generator import generate
