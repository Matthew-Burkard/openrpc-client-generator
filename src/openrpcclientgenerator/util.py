import re
from typing import Optional

from openrpc.objects import OpenRPCObject, SchemaObject


def to_snake_case(string: str) -> str:
    return re.sub(r"(?<!^) ?([A-Z])", r"_\1", string).lower().replace("-", "_")


def to_pascal_case(string: str) -> str:
    string = string.replace("-", " ")
    string = string.replace("_", " ")
    return "".join(s[0].upper() + s[1:] for s in string.split(" "))


def to_camel_case(string: str) -> str:
    string = string.title().replace("_", "")
    if len(string) > 0:
        string = string[0].lower() + string[1:]
    return string


def plural(word: str) -> str:
    if re.search(r"([sxz]$|[^aeioudgkprt]h$)", word, re.I):
        return f"{word}es"
    if re.search(r"[^aeiou]y$", word, re.I):
        return re.sub(r"y$", "ies", word)
    return f"{word}s"


def get_schemas(schemas: dict[str, SchemaObject]) -> dict[str, SchemaObject]:
    schemas = schemas or {}
    for name, schema in schemas.items():
        if schema.definitions:
            schemas = {**schemas, **get_schemas(schema.definitions)}
    return schemas
