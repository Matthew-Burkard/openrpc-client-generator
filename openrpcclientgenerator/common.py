"""Shared functionality across library."""
from typing import Union

import caseswitcher as cs
from openrpc import ServerObject


def get_servers(servers: Union[list[ServerObject], ServerObject]) -> dict[str, str]:
    """Get map of server name to URL."""
    if isinstance(servers, list):
        return {f"{cs.to_upper_snake(s.name)}": f"{s.url}" for s in servers}
    return {f"{cs.to_upper_snake(servers.name)}": f"{servers.url}"}