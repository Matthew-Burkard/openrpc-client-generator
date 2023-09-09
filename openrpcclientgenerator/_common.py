"""Shared components."""
from __future__ import annotations

import string
from enum import Enum
from pathlib import Path
from typing import Any

import caseswitcher
from openrpc import Method
from pydantic import BaseModel, Field


class Language(Enum):
    """Client language options."""

    PYTHON = "py"
    TYPESCRIPT = "ts"


class RPCGroup(BaseModel):
    """Group RPC methods by `.` separator."""

    name: str
    methods: dict[str, Method] = Field(default_factory=dict)
    child_groups: dict[str, "RPCGroup"] = Field(default_factory=dict)


def get_rpc_group(client_name: str, methods: list[Method]) -> RPCGroup:
    """Get RPC methods by group.

    Groups methods by `.` character in method name. So methods
    `math.add` and `math.subtract` will both be grouped in `math` group.
    This is to create a client where the syntax to call method
    `math.add` will be `client.math.add` since a child class was made
    for the group.

    :param client_name: Name of the client. Generated client will be
        `f"{client_name}Client"`.
    :param methods: Methods of the RPC server.
    :return:
    """
    group = RPCGroup(name=client_name)
    valid = string.ascii_lowercase + string.ascii_uppercase + string.digits + "_"
    for method in methods:
        children = method.name.split(".")
        current_group = group
        for i, child in enumerate(children):
            child_name = "".join(c if c in valid else "_" for c in child)
            if child_name and child_name[0] in string.digits:
                child_name = f"n{child_name}"
            child_name = child_name or "method"
            if i + 1 == len(children):
                current_group.methods[child_name] = method
                continue
            if not current_group.child_groups.get(child_name):
                new_group = RPCGroup(name=child_name)
                current_group.child_groups[child_name] = new_group
            current_group = current_group.child_groups[child_name]
    return group


def get_enum_option_name(option: Any) -> str:
    """Get a name for an enum option."""
    if isinstance(option, str):
        return caseswitcher.to_snake(option).upper()
    return f"NUMBER_{option}"


def get_enum_value(value: Any) -> str:
    """Get the value for an enum option."""
    if isinstance(value, str):
        return f'"{value}"'
    return value


def touch_and_write(path: Path, content: str) -> None:
    """Create a file and write text to it."""
    path.touch(exist_ok=True)
    path.write_text(content)
