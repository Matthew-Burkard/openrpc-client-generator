"""Generate Python client."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import black
import caseswitcher
import isort
from jinja2 import Environment, FileSystemLoader
from openrpc import Info, Method, OpenRPC, Schema, SchemaType

from openrpcclientgenerator import _common as common

root = Path(__file__).parent
templates = root.joinpath("templates")
env = Environment(  # noqa: S701
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
    None: "Any",
}


def generate_client(rpc: OpenRPC, url: str, transport: str, out: Path) -> None:
    """Generate a Python client."""
    # Create client directory adn src directory.
    out.mkdir(exist_ok=True)
    py_out = out.joinpath("python")
    py_out.mkdir(exist_ok=True)
    client_dir = py_out.joinpath(caseswitcher.to_kebab(f"{rpc.info.title}-client"))
    client_dir.mkdir(exist_ok=True)
    src_dir = client_dir.joinpath(caseswitcher.to_snake(f"{rpc.info.title}_client"))
    src_dir.mkdir(exist_ok=True)
    # Create Python files.
    schemas = (rpc.components.schemas if rpc.components is not None else {}) or {}
    client = _get_client(rpc.info.title, rpc.methods, schemas, url, transport)
    common.touch_and_write(src_dir.joinpath("client.py"), client)
    models = _get_models(schemas)
    common.touch_and_write(src_dir.joinpath("models.py"), models)
    src_dir.joinpath("__init__.py").touch(exist_ok=True)
    # Create setup and README files.
    common.touch_and_write(
        client_dir.joinpath("setup.py"), _get_setup(rpc.info, transport)
    )
    common.touch_and_write(
        client_dir.joinpath("README.md"), _get_readme(rpc.info.title, transport)
    )


def _get_client(
    title: str,
    methods: list[Method],
    schemas: dict[str, SchemaType],
    url: str,
    transport: str,
) -> str:
    group = common.get_rpc_group(caseswitcher.to_pascal(title), methods)
    template = env.get_template("python/client_module.j2")
    context = {
        "imports": ", ".join(schemas),
        "transport": transport,
        "group": group,
        "indent": "",
        "py_type": py_type,
        "cs": caseswitcher,
        "url": url,
    }
    return black.format_str(isort.code(template.render(context)), mode=black_mode)


def _get_models(schemas: dict[str, SchemaType]) -> str:
    context = {
        "schemas": schemas,
        "py_type": py_type,
        "cs": caseswitcher,
        "get_enum_option_name": common.get_enum_option_name,
        "get_enum_value": common.get_enum_value,
    }
    template = env.get_template("python/models.j2")
    return black.format_str(isort.code(template.render(context)), mode=black_mode)


def _get_setup(info: Info, transport: str) -> str:
    context = {
        "project_name": caseswitcher.to_kebab(info.title) + "-client",
        "project_dir": caseswitcher.to_snake(info.title) + "_client",
        "project_title": caseswitcher.to_title(info.title),
        "info": info,
        "transport": transport,
    }
    return env.get_template("python/setup.j2").render(context) + "\n"


def _get_readme(rpc_title: str, transport: str) -> str:
    template = env.get_template("python/readme.j2")
    context = {
        "project_title": caseswitcher.to_title(rpc_title),
        "package_name": caseswitcher.to_snake(rpc_title) + "_client",
        "client_name": caseswitcher.to_pascal(rpc_title),
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
        return _get_schema_from_type(schema)
    if schema_list := schema.all_of or schema.any_of or schema.one_of:
        return " | ".join(py_type(it) for it in schema_list)
    if schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "Any"


def _get_schema_from_type(schema: Schema) -> str:
    if schema.type == "array":
        return _get_array_type(schema)
    if schema.type == "object":
        return f"dict[str, {py_type(schema.additional_properties)}]"
    if isinstance(schema.type, list):
        return " | ".join(type_map[it] for it in schema.type)
    if schema.type == "string" and schema.format:
        return _get_str_type(schema.format)
    return type_map[schema.type]


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


def _get_const_type(const_value: Any) -> str:
    const = f'"{const_value}"' if isinstance(const_value, str) else const_value
    return f"Literal[{const}]"


def _get_array_type(schema: Schema) -> str:
    if "prefix_items" in schema.model_fields_set:
        types = ", ".join(
            py_type(prefix_item) for prefix_item in schema.prefix_items or []
        )
        return f"tuple[{types}]"
    collection_type = "set" if schema.unique_items else "list"
    return f"{collection_type}[{py_type(schema.items)}]"
