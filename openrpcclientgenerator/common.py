"""Shared components."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import caseswitcher
from openrpc import Method
from pydantic import BaseModel, Field


class RPCGroup(BaseModel):
    """Group RPC methods by `.` separator."""

    name: str
    title: str
    methods: list[Method] = Field(default_factory=list)
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
    group = RPCGroup(title=client_name, name=caseswitcher.to_snake(client_name))
    for method in methods:
        children = method.name.split(".")
        current_group = group
        for i, child in enumerate(children):
            if i + 1 == len(children):
                new_method = copy.copy(method)
                new_method.name = child
                current_group.methods.append(new_method)
                continue
            title = caseswitcher.to_pascal(child)
            if not current_group.child_groups.get(title):
                new_group = RPCGroup(name=child, title=title)
                current_group.child_groups[title] = new_group
            current_group = current_group.child_groups[title]
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
