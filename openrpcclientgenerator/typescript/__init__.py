"""Generate TypeScript content."""

__all__ = (
    "get_client",
    "get_models",
    "get_index_ts",
    "get_package_json",
    "get_ts_config",
)

from openrpcclientgenerator.typescript._get_client import get_client
from openrpcclientgenerator.typescript._get_models import get_models
from openrpcclientgenerator.typescript._project_files import (
    get_index_ts,
    get_package_json,
    get_ts_config,
)
