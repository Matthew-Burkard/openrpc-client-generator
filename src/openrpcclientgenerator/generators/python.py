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
            "object": "dict[str, Any]",
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

            # Get method arguments.
            args = []
            for param in method.params:
                p_type = self._get_py_type(param.json_schema)
                if not param.required and not p_type.startswith("Optional"):
                    p_type = f"Optional[{p_type}]"
                if p_type.startswith("Optional"):
                    p_type += " = None"
                args.append(f", {param.name}: {p_type}")
            args.sort(key=lambda x: str(x).find("Optional") != -1)

            # Get return type and add code to deserialize results.
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
            ),
        )

    def _get_py_type(self, schema: SchemaObject) -> str:
        # Get Python type from JSON Schema type.

        def get_union_type_from_strings(types: list[str]) -> str:
            if len(types) == 2 and "null" in types:
                types.remove("null")
                return f"Optional[{self._type_map[types[0]]}]"
            if "null" in types:
                types.remove("null")
                type_str = ", ".join(self._type_map[it] for it in types)
                return f"Optional[Union[{type_str}]]"
            return f"Union[{', '.join(self._type_map[it] for it in types)}]"

        def get_union_type_from_schemas(types: list[SchemaObject]) -> str:
            str_types = [
                self._get_py_type(it)
                if isinstance(it, SchemaObject)
                else self._type_map[it]
                for it in types
            ]
            if len(str_types) == 2 and "None" in str_types:
                str_types.remove("None")
                return f"Optional[{str_types[0]}]"
            if "None" in str_types:
                str_types.remove("None")
                return f"Optional[Union[{', '.join(str_types)}]]"
            return f"Union[{', '.join(str_types)}]"

        if schema.type:
            if schema.type == "array":
                return f"list[{self._get_py_type(schema.items)}]"
            elif schema.type == "object":
                v_type = self._get_py_type(schema.items) if schema.items else "Any"
                return f"dict[str, {v_type}]"
            elif isinstance(schema.type, list):
                return get_union_type_from_strings(schema.type)
            return self._type_map[schema.type]
        elif schema_list := schema.all_of or schema.any_of or schema.one_of:
            return get_union_type_from_schemas(schema_list)
        elif schema.ref:
            return f'"{schema.ref.removeprefix("#/components/schemas/")}"'

        return "Any"
