"""Shared Python properties."""
import re

from openrpc import SchemaObject

type_map = {
    "boolean": "bool",
    "integer": "int",
    "number": "float",
    "string": "str",
    "null": "None",
    "object": "dict[str, Any]",
}

indent = " " * 4


def get_py_type(schema: SchemaObject) -> str:
    """Get Python type from JSON Schema type."""

    def _get_union_type_from_strings(types: list[str]) -> str:
        if len(types) == 2 and "null" in types:
            types.remove("null")
            return f"Optional[{type_map[types[0]]}]"
        if "null" in types:
            types.remove("null")
            type_str = ", ".join(type_map[it] for it in types)
            return f"Optional[Union[{type_str}]]"
        return f"Union[{', '.join(type_map[it] for it in types)}]"

    def _get_union_type_from_schemas(types: list[SchemaObject]) -> str:
        str_types = [get_py_type(it) for it in types]
        if len(str_types) == 2 and "None" in str_types:
            str_types.remove("None")
            return f"Optional[{str_types[0]}]"
        if "None" in str_types:
            str_types.remove("None")
            return f"Optional[Union[{', '.join(str_types)}]]"
        return f"Union[{', '.join(str_types)}]"

    if schema is None:
        return "Any"

    if schema.type:
        if schema.type == "array":
            return f"list[{get_py_type(schema.items)}]"
        if schema.type == "object":
            v_type = get_py_type(schema.items) if schema.items else "Any"
            return f"dict[str, {v_type}]"
        if isinstance(schema.type, list):
            return _get_union_type_from_strings(schema.type)
        if schema.type == "string" and schema.format:
            return {"binary": "bytes"}.get(schema.format) or "str"
        return type_map[schema.type]
    if schema_list := schema.all_of or schema.any_of or schema.one_of:
        return _get_union_type_from_schemas(schema_list)
    if schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return "Any"
