import re
from dataclasses import dataclass

from openrpc.objects import MethodObject, SchemaObject

from openrpcclientgenerator import util
from openrpcclientgenerator.templates.csharp import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


class CSharpGenerator:
    def __init__(
        self, title: str, methods: list[MethodObject], schemas: dict[str, SchemaObject]
    ) -> None:
        self.title = title
        self.methods = methods
        self.schemas = schemas
        self._models: list[str] = []
        self._type_map = {
            "integer": "int",
            "number": "double",
            "boolean": "bool",
            "string": "string",
        }
        self._indent = " " * 4

    def get_methods(self) -> str:
        def get_type(schema: SchemaObject) -> str:
            # Get C# type from JSON Schema type.
            if schema.type:
                if schema.type == "array":
                    if st := schema.items.type:
                        return f"List<{st}>"
                    key = re.search(r"([^/]+)$", schema.items.ref).group(1)
                    return f"List<{self.schemas[key].title}>"
                elif schema.type == "object":
                    return "Dictionary<string, object>"
                # Type must be a primitive type.
                return self._type_map.get(schema.type) or schema.title
            elif schema.any_of:
                ret_val = " | ".join(get_type(it) or "null" for it in schema.any_of)
            # TODO all_of, one_of
            else:
                key = re.search(r"([^/]+)$", schema.ref).group(1)
                ret_val = self.schemas[key].title
            if ret_val:
                return util.to_pascal_case(ret_val)

        def get_method(method: MethodObject) -> str:
            if len(method.params) > 1:
                params = ", ".join(util.to_camel_case(it.name) for it in method.params)
                params = f"new List<object> {{{params}}}"
            else:
                # Length is 1 or 0.
                params = "".join(util.to_camel_case(it.name) for it in method.params)

            if method.description:
                # TODO Use recommended xml (oof).
                doc = f"\n{self._indent * 2}".join(
                    f" * {line.strip()}".rstrip()
                    for line in method.description.split("\n")
                )
            else:
                doc = " * No description provided."
            return code.method.format(
                doc=doc,
                return_type=get_type(method.result.json_schema),
                name=util.to_pascal_case(re.sub(r".*?\.", "", method.name)),
                args=", ".join(
                    f"{get_type(it.json_schema)}" f" {util.to_camel_case(it.name)}"
                    for it in method.params
                ),
                method=method.name,
                params=params,
            )

        return code.client_file.format(
            namespace=f"{util.to_pascal_case(self.title)}Client",
            title=util.to_pascal_case(self.title),
            transport="Http",
            methods="\n".join(get_method(m) for m in self.methods),
        ).lstrip()

    def get_models(self) -> str:
        models = [
            self._get_model(name, schema) for name, schema in self.schemas.items()
        ]
        return code.class_file.format(
            namespace=f"{util.to_pascal_case(self.title)}Client",
            classes="\n".join(
                code.data_class.format(
                    name=m.name,
                    doc=m.doc,
                    fields=f"\n{self._indent * 2}".join(m.fields),
                )
                for m in models
            ),
        ).lstrip()

    def _get_model(self, name: str, schema: SchemaObject) -> _Model:
        fields = []
        for prop_name, prop in schema.properties.items():
            c_sharp_type = ""
            # This should be recursive.
            if prop.ref:
                c_sharp_type = util.to_pascal_case(
                    re.search(r"([^/]+)$", prop.ref).group(1)
                )
            elif prop.type == "object":
                if not c_sharp_type:
                    c_sharp_type = "Dictionary<string, object>"
            elif prop.type == "array":
                c_sharp_type = f"List<{self._type_map[prop.items.type]}>"
            elif isinstance(prop.type, list):
                # TODO Proper C# union type.
                c_sharp_type = "object"
            else:
                c_sharp_type = self._type_map[prop.type]

            if prop_name in (prop.required or []):
                required = ", Required = Required.Always"
            else:
                required = ""
                if c_sharp_type in ["int", "double", "bool"]:
                    c_sharp_type = f"{c_sharp_type}?"

            fields.append(
                code.field.format(
                    name=prop_name,
                    type=c_sharp_type,
                    prop_name=util.to_pascal_case(prop_name),
                    req=required,
                )
            )
        if schema.description:
            doc = f"\n{self._indent} * ".join(
                line.strip() for line in schema.description.split("\n")
            )
            # Remove trailing spaces from blank lines.
            doc = "\n".join(line.rstrip() for line in doc.split("\n"))
        else:
            doc = f"{name} object."
        # This fixes single line doc strings.
        if "\n" not in doc:
            doc += f"\n{self._indent} *"
        doc = f"/**\n{self._indent} * {doc.rstrip()}/"
        return _Model(name, doc, fields)
