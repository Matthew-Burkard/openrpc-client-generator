import re
from dataclasses import dataclass, field

from openrpc.objects import MethodObject, SchemaObject

from openrpcclientgenerator.templates.python import code


@dataclass
class _Model:
    name: str
    args: list[str] = field(default_factory=lambda: [])
    fields: list[str] = field(default_factory=lambda: [])


class KotlinGenerator:
    def __init__(
        self, title: str, methods: list[MethodObject], schemas: dict[str, SchemaObject]
    ) -> None:
        self.title = title
        self.methods = methods
        self.schemas = schemas
        self._models: list[str] = []
        self._type_map = {
            "boolean": "Boolean",
            "integer": "Int",
            "number": "Double",
            "string": "String",
            "null": "null",
            "object": "Map<String, Any>",
        }
        self._indent = " " * 2

    def get_methods(self, transport: str = "HTTP") -> str:
        def get_method(method: MethodObject) -> str:
            return code.method.format()

        return code.client_file.format()

    def get_models(self) -> str:
        def get_model(name: str, schema: SchemaObject) -> _Model:
            return _Model()

        return code.model_file.format()

    def _get_kotlin_type(self, schema: SchemaObject) -> str:
        # Get Kotlin type from JSON Schema type.
        if schema is None:
            return "Any"

        if schema.type:
            if schema.type == "array":
                return f"List<{self._get_kotlin_type(schema.items)}>"
            elif schema.type == "object":
                v_type = self._get_kotlin_type(schema.items) if schema.items else "Any"
                return f"Map<String, {v_type}>"
            elif isinstance(schema.type, list):
                types = " | ".join(self._type_map[it] for it in schema.type)
                return f"dynamic /* {types} */"
            # TODO Class with ByteArray should override equals and hashCode.
            if schema.type == "string" and schema.format:
                return {"binary": "ByteArray"}.get(schema.format) or "String"
            return self._type_map[schema.type]
        elif schema_list := schema.all_of or schema.any_of or schema.one_of:
            types = " | ".join(self._get_kotlin_type(it) for it in schema_list)
            return f"dynamic /* {types} */"
        elif schema.ref:
            return re.sub(r"#/.*/(.*)", r"\1", schema.ref)
        return "Any"
