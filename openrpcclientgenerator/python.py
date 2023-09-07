"""Generate Python client."""
import re
from pathlib import Path

import black
import caseswitcher
from jinja2 import Environment, FileSystemLoader
from openrpc import OpenRPC, Schema

from openrpcclientgenerator import common

root = Path(__file__).parent
templates = root.joinpath("templates")
type_map = {
    "boolean": "bool",
    "integer": "int",
    "number": "float",
    "string": "str",
    "null": "None",
    "object": "dict[str, Any]",
}


def generate_client(rpc: OpenRPC, transport: str) -> None:
    """Generate a Python client."""
    group = common.get_rpc_group(caseswitcher.to_pascal(rpc.info.title), rpc.methods)
    env = Environment(
        loader=FileSystemLoader(templates), lstrip_blocks=True, trim_blocks=True
    )
    template = env.get_template("python/client_module.j2")
    context = {
        "transport": transport,
        "group": group,
        "indent": "",
        "py_type": py_type,
    }
    rendered_template = template.render(context)
    print(
        black.format_str(rendered_template, mode=black.Mode(magic_trailing_comma=False))
    )


def py_type(schema: Schema) -> str:
    """Get Python type from JSON Schema type."""
    if schema is None or schema is True:
        return "Any"

    if schema.type:
        if schema.type == "array":
            return f"list[{py_type(schema.items)}]"
        elif schema.type == "object":
            v_type = py_type(schema.items) if schema.items else "Any"
            return f"dict[str, {v_type}]"
        elif isinstance(schema.type, list):
            return " | ".join(type_map[it] for it in schema.type)
        if schema.type == "string" and schema.format:
            return {"binary": "bytes"}.get(schema.format) or "str"
        return type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        str_types = [py_type(it) for it in schema_list]
        return " | ".join(type_map[it] for it in str_types)
    elif schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "Any"

