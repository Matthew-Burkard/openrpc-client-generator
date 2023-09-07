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


def generate_client(rpc: OpenRPC, transport: str, out: Path) -> None:
    """Generate a Python client."""
    out.mkdir(exist_ok=True)
    client, models = _get_code(rpc, transport)
    client_path = out.joinpath(caseswitcher.to_kebab(f"{rpc.info.title}-client"))
    client_path.mkdir(exist_ok=True)
    src_dir = client_path.joinpath(caseswitcher.to_snake(f"{rpc.info.title}_client"))
    src_dir.mkdir(exist_ok=True)
    client_file = src_dir.joinpath("client.py")
    client_file.touch(exist_ok=True)
    client_file.write_text(client)
    models_file = src_dir.joinpath("models.py")
    models_file.touch(exist_ok=True)
    models_file.write_text(models)


def _get_code(rpc: OpenRPC, transport: str) -> tuple[str, str]:
    group = common.get_rpc_group(caseswitcher.to_pascal(rpc.info.title), rpc.methods)
    env = Environment(
        loader=FileSystemLoader(templates), lstrip_blocks=True, trim_blocks=True
    )
    client_template = env.get_template("python/client_module.j2")
    context = {"transport": transport, "group": group, "indent": "", "py_type": py_type}
    client = black.format_str(
        client_template.render(context), mode=black.Mode(magic_trailing_comma=False)
    )
    context = {
        "schemas": rpc.components.schemas,
        "py_type": py_type,
        "cs": caseswitcher,
    }
    models_template = env.get_template("python/models.j2")
    models = black.format_str(
        models_template.render(context), mode=black.Mode(magic_trailing_comma=False)
    )
    return client, models


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
        return " | ".join(str_types)
    elif schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "Any"

