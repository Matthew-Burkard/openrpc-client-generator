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
_NUM_TYPES_IN_OPTIONAL_TYPE = 2


def get_py_type(schema: SchemaObject) -> str:
    """Get Python type from JSON Schema type."""
    if schema is None:
        return "Any"

    type_ = "Any"
    if schema.type:
        if schema.type == "array":
            type_ = f"list[{get_py_type(schema.items)}]"
        elif schema.type == "object":
            v_type = get_py_type(schema.items) if schema.items else "Any"
            type_ = f"dict[str, {v_type}]"
        elif isinstance(schema.type, list):
            type_ = _get_union_type_from_strings(schema.type)
        elif schema.type == "string" and schema.format:
            type_ = {"binary": "bytes"}.get(schema.format) or "str"
        else:
            type_ = type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        type_ = _get_union_type_from_schemas(schema_list)
    elif schema.ref:
        type_ = re.sub(r"#/.*/(.*)", r"\1", schema.ref)

    return type_


def _get_union_type_from_strings(types: list[str]) -> str:
    if len(types) == _NUM_TYPES_IN_OPTIONAL_TYPE and "null" in types:
        types.remove("null")
        return f"Optional[{type_map[types[0]]}]"
    if "null" in types:
        types.remove("null")
        type_str = ", ".join(type_map[it] for it in types)
        return f"Optional[Union[{type_str}]]"
    return f"Union[{', '.join(type_map[it] for it in types)}]"


def _get_union_type_from_schemas(types: list[SchemaObject]) -> str:
    str_types = [get_py_type(it) for it in types]
    if len(str_types) == _NUM_TYPES_IN_OPTIONAL_TYPE and "None" in str_types:
        str_types.remove("None")
        return f"Optional[{str_types[0]}]"
    if "None" in str_types:
        str_types.remove("None")
        return f"Optional[Union[{', '.join(str_types)}]]"
    return f"Union[{', '.join(str_types)}]"
