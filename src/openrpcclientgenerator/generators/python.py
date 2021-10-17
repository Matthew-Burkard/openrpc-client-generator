import re
from dataclasses import dataclass

from openrpc.objects import MethodObject, SchemaObject

from openrpcclientgenerator import util
from openrpcclientgenerator.templates.python import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


class PythonGenerator:
    def __init__(
        self, title: str, methods: list[MethodObject], schemas: dict[str, SchemaObject]
    ) -> None:
        self.title = title
        self.methods = methods
        self.schemas = schemas
        self._models: list[str] = []
        self._type_map = {
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "string": "str",
            "null": "None",
        }
        self._indent = " " * 4

    def get_methods(self, transport: str = "HTTP") -> str:
        _all = []

        def get_method(method: MethodObject) -> str:
            if len(method.params) > 1:
                params = ", ".join(util.to_snake_case(it.name) for it in method.params)
            else:
                # Length is 1 or 0.
                params = "".join(util.to_snake_case(it.name) for it in method.params)
            args = [
                f", {p.name}: {self._get_py_type(p.json_schema)}" for p in method.params
            ]
            args = [re.sub(r"(Optional.*)", r"\1 = None", arg) for arg in args]
            args.sort(key=lambda x: str(x).find("Optional") != -1)
            return_type = self._get_py_type(method.result.json_schema)
            if return_type.startswith("list["):
                # FIXME Won't work with union types.
                deserialize = code.deserialize_list.format(
                    type=return_type.removeprefix("list[").removesuffix("]")
                )
            else:
                deserialize = code.deserialize_class.format(return_type=return_type)
            return code.method.format(
                name=util.to_snake_case(re.sub(r".*?\.", "", method.name)),
                method=method.name,
                args="self" + "".join(args),
                return_type=return_type,
                doc=f'"""{method.description}"""',
                params=params,
                deserialize=deserialize,
            )

        return code.client_file.format(
            title=util.to_pascal_case(self.title),
            transport=transport,
            methods="".join(get_method(m) for m in self.methods),
        )

    def get_models(self) -> str:
        _all = []

        def get_model(name: str, schema: SchemaObject) -> _Model:
            fields = []
            for n, prop in schema.properties.items():
                default = " = None" if n in (schema.required or []) else ""
                fields.append(
                    code.field.format(
                        name=n,
                        type=self._get_py_type(prop),
                        default=default,
                    )
                )
            if schema.description:
                doc = f"\n{self._indent}".join(
                    line.strip() for line in schema.description.split("\n")
                )
                # Remove trailing spaces from blank lines.
                doc = "\n".join(line.rstrip() for line in doc.split("\n"))
            else:
                doc = f"{schema.title} object."
            if len(doc.split("\n")) > 1:
                doc += self._indent

            fields.sort(key=lambda x: x.endswith(" = None"))
            fields = [
                re.sub(r": (.*?) =", r": Optional[\1] =", field)
                if field.endswith(" = None")
                else field
                for field in fields
            ]
            _all.append(name)
            return _Model(
                name=name,
                doc=f'"""{doc}"""',
                fields=fields,
            )

        models = [get_model(name, schema) for name, schema in self.schemas.items()]
        return code.model_file.format(
            all=", ".join(f'"{it}"' for it in _all),
            classes="\n".join(
                code.data_class.format(
                    name=model.name,
                    doc=model.doc,
                    fields=f"\n{self._indent}".join(model.fields),
                )
                for model in models
            )
        )

    def _get_py_type(self, schema: SchemaObject) -> str:
        # Get Python type from JSON Schema type.
        if schema.type:
            if schema.type == "array":
                return f"list[{self._get_py_type(schema.items)}]"
            elif schema.type == "object":
                v_type = self._get_py_type(schema.items) if schema.items else "Any"
                return f"dict[str, {v_type}]"
            else:
                if isinstance(schema.type, list):
                    return f"Union[{', '.join(self._type_map[t] for t in schema.type)}]"
                return self._type_map[schema.type]
        elif schema_list := schema.any_of or schema.all_of or schema.any_of:
            union = ", ".join(
                self._get_py_type(it)
                if isinstance(it, SchemaObject)
                else self._type_map[it]
                for it in schema_list
            )
            return f"Union[{union}]"
        elif schema.ref:
            return schema.ref.removeprefix("#/components/schemas/")
        else:
            return "Any"
