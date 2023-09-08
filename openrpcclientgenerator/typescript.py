"""Generate TypeScript client."""
from pathlib import Path

import caseswitcher
from jinja2 import Environment, FileSystemLoader
from openrpc import Method, OpenRPC, SchemaType

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
    return schema.type
