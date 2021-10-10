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
        def get_type(schema: SchemaObject) -> str:
            # Get Python type from JSON Schema type.
            if schema.type:
                if schema.type == "array":
                    return_type = f"list[{get_type(schema.items)}]"
                elif schema.type == "object":
                    v_type = get_type(schema.items) if schema.items else "Any"
                    return_type = f"dict[str, {v_type}]"
                else:
                    return_type = self._type_map[schema.type]
            elif schema.any_of:
                return_type = ", ".join(get_type(it) for it in schema.any_of)
                return_type = f"Union[{return_type}]"
                if re.search(r", None", return_type):
                    if len(schema.any_of) == 2:
                        return_type = re.sub(
                            r"Union\[([^,]+), None]", r"Optional[\1]", return_type
                        )
                    else:
                        return_type = f"Optional[{return_type}]"
            # TODO all_of, one_of
            else:
                return_type = schema.ref.removeprefix("#/components/schemas/")
            return return_type

        def get_method(method: MethodObject) -> str:
            if len(method.params) > 1:
                params = ", ".join(util.to_snake_case(it.name) for it in method.params)
            else:
                # Length is 1 or 0.
                params = "".join(util.to_snake_case(it.name) for it in method.params)
            args = [f", {p.name}: {get_type(p.json_schema)}" for p in method.params]
            args = [re.sub(r"(Optional.*)", r"\1 = None", arg) for arg in args]
            args.sort(key=lambda x: str(x).find("Optional") != -1)
            return_type = get_type(method.result.json_schema)
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
        models = [
            self._get_model(name, schema) for name, schema in self.schemas.items()
        ]
        # for name, schema in self.schemas.items():
        return code.model_file.format(
            classes="\n".join(
                code.data_class.format(
                    name=model.name,
                    doc=model.doc,
                    fields=f"\n{self._indent}".join(model.fields),
                )
                for model in models
            )
        )

    def _get_model(self, name: str, schema: SchemaObject) -> _Model:
        fields = []
        for n, prop in schema.properties.items():
            default = " = None" if n in (schema.required or []) else ""
            if prop.type:
                field_type = self._type_map[prop.type]
            else:
                field_type = prop.ref.removeprefix("#/components/schemas/")
                # FIXME Remove quotes on py3.10
                field_type = f"'{field_type}'"
            fields.append(
                code.field.format(
                    name=n,
                    type=field_type,
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
        return _Model(
            name=name,
            doc=f'"""{doc}"""',
            fields=fields,
        )
