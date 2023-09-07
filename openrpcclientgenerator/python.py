"""Generate Python client."""
import re
from pathlib import Path

import black
import caseswitcher
import httpx
import isort
from jinja2 import Environment, FileSystemLoader
from openrpc import OpenRPC, Schema, SchemaType

from openrpcclientgenerator import common

root = Path(__file__).parent
templates = root.joinpath("templates")
env = Environment(
    loader=FileSystemLoader(templates), lstrip_blocks=True, trim_blocks=True
)
black_mode = black.Mode(magic_trailing_comma=False)
type_map = {
    "boolean": "bool",
    "integer": "int",
    "number": "float",
    "string": "str",
    "null": "None",
    "object": "dict[str, Any]",
}


def generate_client(rpc: OpenRPC, url: str, transport: str, out: Path) -> None:
    """Generate a Python client."""
    out.mkdir(exist_ok=True)
    client = _get_client(rpc, url, transport)
    models = _get_models(rpc.components.schemas)
    client_dir = out.joinpath(caseswitcher.to_kebab(f"{rpc.info.title}-client"))
    client_dir.mkdir(exist_ok=True)
    src_dir = client_dir.joinpath(caseswitcher.to_snake(f"{rpc.info.title}_client"))
    src_dir.mkdir(exist_ok=True)
    common.touch_and_write(src_dir.joinpath("client.py"), client)
    common.touch_and_write(src_dir.joinpath("models.py"), models)
    src_dir.joinpath("__init__.py").touch(exist_ok=True)
    common.touch_and_write(
        client_dir.joinpath("setup.py"),
        _get_setup(rpc.info.title, rpc.info.version, transport),
    )


def _get_client(rpc: OpenRPC, url: str, transport: str) -> tuple[str, str]:
    group = common.get_rpc_group(caseswitcher.to_pascal(rpc.info.title), rpc.methods)
    template = env.get_template("python/client_module.j2")
    context = {
        "transport": transport,
        "group": group,
        "indent": "",
        "py_type": py_type,
        "cs": caseswitcher,
        "url": url,
    }
    client = black.format_str(isort.code(template.render(context)), mode=black_mode)
    return client


def _get_models(schemas: dict[str, Schema]) -> tuple[str, str]:
    context = {
        "schemas": schemas,
        "py_type": py_type,
        "cs": caseswitcher,
        "get_enum_option_name": common.get_enum_option_name,
    }
    template = env.get_template("python/models.j2")
    models = black.format_str(isort.code(template.render(context)), mode=black_mode)
    return models


def _get_setup(rpc_title: str, version: str, transport: str) -> str:
    template = env.get_template("python/setup.j2")
    context = {
        "project_name": caseswitcher.to_kebab(rpc_title) + "-client",
        "project_dir": caseswitcher.to_snake(rpc_title) + "_client",
        "project_title": caseswitcher.to_title(rpc_title),
        "version": version,
        "transport": transport,
    }
    return template.render(context) + "\n"


def py_type(schema: SchemaType | None) -> str:
    """Get Python type from JSON Schema type."""
    if schema is None or isinstance(schema, bool):
        return "Any"

    if "const" in schema.model_fields_set:
        return _get_const_type(schema.const)
    if schema.type:
        if schema.type == "array":
            return _get_array_type(schema)
        elif schema.type == "object":
            return _get_object_type(schema)
        elif isinstance(schema.type, list):
            return " | ".join(type_map[it] for it in schema.type)
        if schema.type == "string" and schema.format:
            return _get_str_type(schema.format)
        return type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        return " | ".join(py_type(it) for it in schema_list)
    elif schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "Any"


def _get_str_type(str_format: str) -> str:
    return {
        "binary": "bytes",
        "date": "datetime.date",
        "time": "datetime.time",
        "date-time": "datetime.datetime",
        "duration": "datetime.timedelta",
        "uuid": "UUID",
        "uuid1": "UUID1",
        "uuid3": "UUID3",
        "uuid4": "UUID4",
        "uuid5": "UUID5",
    }.get(str_format) or "str"


def _get_const_type(const_value: str) -> str:
    if not isinstance(const_value, str):
        const = const_value
    else:
        const = f'"{const_value}"'
    return f"Literal[{const}]"


def _get_object_type(schema: Schema) -> str:
    v_type = (
        py_type(schema.additional_properties) if schema.additional_properties else "Any"
    )
    return f"dict[str, {v_type}]"


def _get_array_type(schema: Schema) -> str:
    if "prefix_items" in schema.model_fields_set:
        types = ", ".join(py_type(prefix_item) for prefix_item in schema.prefix_items)
        return f"tuple[{types}]"
    collection_type = "set" if schema.unique_items else "list"
    return f"{collection_type}[{py_type(schema.items)}]"


if __name__ == "__main__":
    resp = httpx.get("http://localhost:8000/openrpc.json")
    generate_client(
        OpenRPC(**resp.json()),
        "ws://localhost:8000/api/v1",
        "WS",
        root.parent.joinpath("build"),
    )
