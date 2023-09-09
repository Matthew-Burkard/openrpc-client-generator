"""Generate TypeScript client."""
import re
from pathlib import Path
from typing import Any

import caseswitcher
from jinja2 import Environment, FileSystemLoader
from openrpc import Info, Method, OpenRPC, Schema, SchemaType

from openrpcclientgenerator import _common as common

root = Path(__file__).parent
templates = root.joinpath("templates")
env = Environment(  # noqa: S701
    loader=FileSystemLoader(templates), lstrip_blocks=True, trim_blocks=True
)
ts_config = """
{
  "compilerOptions": {
    "outDir": "dist",
    "target": "es2020",
    "module": "es2020",
    "rootDir": "src",
    "moduleResolution": "Node",
    "declaration": true,
    "removeComments": true,
    "experimentalDecorators": true,
    "noUnusedParameters": false,
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "lib"]
}
"""


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
    common.touch_and_write(src_dir.joinpath("models.ts"), _get_models(schemas))
    common.touch_and_write(
        src_dir.joinpath("index.ts"), _get_index(rpc.info.title, schemas)
    )

    # Create project files.
    common.touch_and_write(
        client_dir.joinpath("package.json"), _get_package_json(rpc.info, transport)
    )
    common.touch_and_write(client_dir.joinpath("tsconfig.json"), ts_config)

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
    context = {
        "imports": "{%s}" % ", ".join(schemas),
        "transport": transport,
        "group": group,
        "ts_type": ts_type,
        "cs": caseswitcher,
        "url": url,
        "skip_methods": '"connect", "close"' if transport == "WS" else "",
    }
    return env.get_template("typescript/client_module.j2").render(context)


def _get_models(schemas: dict[str, SchemaType]) -> str:
    context = {
        "schemas": schemas,
        "ts_type": ts_type,
        "cs": caseswitcher,
        "get_enum_option_name": common.get_enum_option_name,
        "get_enum_value": common.get_enum_value,
    }
    return env.get_template("typescript/models.j2").render(context)


def _get_index(title: str, schemas: dict[str, SchemaType]) -> str:
    models = ", ".join(schemas)
    client = f"{caseswitcher.to_pascal(title)}Client"
    context = {
        "project_dir": caseswitcher.to_snake(title),
        "model_imports": f"{{{models}}}",
        "client_import": f"{{{client}}}",
        "exports": f"{client}, {models}",
    }
    return env.get_template("typescript/index.j2").render(context)


def _get_package_json(info: Info, transport: str) -> str:
    context = {
        "project_name": caseswitcher.to_kebab(info.title) + "-client",
        "project_title": caseswitcher.to_title(info.title),
        "info": info,
        "transport": transport,
    }
    return env.get_template("typescript/package_json.j2").render(context) + "\n"


def _get_readme(rpc_title: str, transport: str) -> str:
    template = env.get_template("python/readme.j2")
    context = {
        "project_title": caseswitcher.to_title(rpc_title),
        "client_import": "{%sClient}" % caseswitcher.to_pascal(rpc_title),
        "package_name": caseswitcher.to_snake(rpc_title) + "_client",
        "client_name": caseswitcher.to_pascal(rpc_title) + "Client",
        "transport": transport,
    }
    return template.render(context) + "\n"


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
