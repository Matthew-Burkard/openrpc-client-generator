"""Shared TypeScript properties."""
import re

from openrpc import SchemaObject

type_map = {
    "boolean": "boolean",
    "integer": "number",
    "number": "number",
    "string": "string",
    "null": "null",
    "object": "object",
}
indent = " " * 2


def get_ts_type(schema: SchemaObject) -> str:
    """Get TypeScript type from JSON Schema."""
    if schema is None:
        return "any"

    type_ = "any"
    if schema.type:
        if schema.type == "array":
            type_ = f"{get_ts_type(schema.items)}[]"
        elif schema.type == "object":
            type_ = "object"
        elif isinstance(schema.type, list):
            type_ = " | ".join(type_map[it] for it in schema.type)
        elif schema.type == "string" and schema.format:
            type_ = {"binary": "any"}.get(schema.format) or "string"
        else:
            type_ = type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        type_ = " | ".join(get_ts_type(it) for it in schema_list)
    elif schema.ref:
        type_ = re.sub(r"#/.*/(.*)", r"\1", schema.ref)
    return type_
