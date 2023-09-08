"""Generate TypeScript client."""
import re
from pathlib import Path
from typing import Any

import caseswitcher
from jinja2 import Environment, FileSystemLoader
from openrpc import Method, OpenRPC, Schema, SchemaType

from openrpcclientgenerator import common

root = Path(__file__).parent
templates = root.joinpath("templates")
env = Environment(  # noqa: S701
    loader=FileSystemLoader(templates), lstrip_blocks=True, trim_blocks=True
)


def generate_client(rpc: OpenRPC, url: str, transport: str, out: Path) -> None:
    """Generate a TypeScript client"""
    out.mkdir(exist_ok=True)
    ts_out = out.joinpath("typescript")
    ts_out.mkdir(exist_ok=True)
    client_dir = ts_out.joinpath(caseswitcher.to_kebab(f"{rpc.info.title}-client"))
    client_dir.mkdir(exist_ok=True)
    src_dir = client_dir.joinpath(caseswitcher.to_snake("src"))
    src_dir.mkdir(exist_ok=True)
    # Create TypeScript files.
    schemas = (rpc.components.schemas if rpc.components is not None else {}) or {}
    client = _get_client(rpc.info.title, rpc.methods, schemas, url, transport)
    common.touch_and_write(src_dir.joinpath("client.ts"), client)


def _get_client(
    title: str,
    methods: list[Method],
    schemas: dict[str, SchemaType],
    url: str,
    transport: str,
) -> str:
    group = common.get_rpc_group(caseswitcher.to_pascal(title), methods)
    template = env.get_template("typescript/client_module.j2")
    context = {
        "transport": transport,
        "group": group,
        "ts_type": ts_type,
        "cs": caseswitcher,
        "url": url,
    }
    return template.render(context)


def ts_type(schema: SchemaType | None) -> str:
    """Get TypeScript type from JSON Schema type."""
    if schema is None or isinstance(schema, bool):
        return "any"
    if "const" in schema.model_fields_set:
        return _get_const_type(schema.const)
    if schema.type:
        return _get_schema_from_type(schema)
    if schema_list := schema.all_of or schema.any_of or schema.one_of:
        return " | ".join(ts_type(it) for it in schema_list)
    if schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "any"

def _get_const_type(const_value: Any) -> str:
    if isinstance(const_value, str):
        return "string"
    # isinstance(const_value, bool) causes issues with values 1 and 0.
    if const_value is True or const_value is False:
        return "boolean"
    if isinstance(const_value, int) or isinstance(const_value, float):
        return "number"
    if const_value is None:
        return "null"
    return "any"

def _get_schema_from_type(schema: Schema) -> str:
    if schema.type == "array":
        return _get_array_type(schema)
    if schema.type == "object":
        return _get_object_type(schema)
    if isinstance(schema.type, list):
        return " | ".join(it if it != "integer" else "number" for it in schema.type)
    return schema.type if schema.type != "integer" else "number"

def _get_array_type(schema: Schema) -> str:
    if "prefix_items" in schema.model_fields_set:
        types = ", ".join(
            ts_type(prefix_item) for prefix_item in schema.prefix_items or []
        )
        return f"[{types}]"
    if schema.unique_items:
        return f"Set<{ts_type(schema.items)}>"
    array_type = ts_type(schema.items)
    if "|" in array_type:
        return f"Array<{ts_type(schema.items)}>"
    return f"{ts_type(schema.items)}[]"


def _get_object_type(schema: Schema) -> str:
    v_type = ts_type(schema.additional_properties)
    if v_type != "any":
        return f"Record<string, {v_type}>"
    return "object"
