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
        return "Any"
