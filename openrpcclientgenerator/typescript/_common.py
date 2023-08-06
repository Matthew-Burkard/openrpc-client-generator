"""Shared typescript properties."""
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
    # Get TypeScript type from JSON Schema type.
    if schema is None:
        return "any"

    if schema.type:
        if schema.type == "array":
            return f"{get_ts_type(schema.items)}[]"
        elif schema.type == "object":
            return "object"
        elif isinstance(schema.type, list):
            return " | ".join(type_map[it] for it in schema.type)
        if schema.type == "string" and schema.format:
            return {"binary": "any"}.get(schema.format) or "string"
        return type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        return " | ".join(get_ts_type(it) for it in schema_list)
    elif schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)
    return "any"
