import re
from dataclasses import dataclass

import caseswitcher as cs
from openrpc.objects import MethodObject, SchemaObject

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
            "boolean": "bool",
            "integer": "int",
            "number": "double",
            "string": "string",
            "null": "null",
            "object": "object",
        }
        self._indent = " " * 4

    def get_methods(self) -> str:
        def get_method(method: MethodObject) -> str:
            if len(method.params) > 1:
                params = ", ".join(cs.to_camel(it.name) for it in method.params)
                params = f"new List<object> {{{params}}}"
            else:
                # Length is 1 or 0.
                params = "".join(cs.to_camel(it.name) for it in method.params)

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
                return_type=self._get_cs_type(method.result.json_schema),
                name=cs.to_pascal(re.sub(r".*?\.", "", method.name)),
                args=", ".join(
                    f"{self._get_cs_type(it.json_schema)} {cs.to_camel(it.name)}"
                    for it in method.params
                ),
                method=method.name,
                params=params,
            )

        return code.client_file.format(
            namespace=f"{cs.to_pascal(self.title)}Client",
            title=cs.to_pascal(self.title),
            transport="Http",
            methods="\n".join(get_method(m) for m in self.methods),
        ).lstrip()

    def get_models(self) -> str:
        def get_model(name: str, schema: SchemaObject) -> _Model:
            fields = []
            for prop_name, prop in schema.properties.items():
                c_sharp_type = self._get_cs_type(prop)

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
                        prop_name=cs.to_pascal(prop_name),
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

        models = [get_model(n, s) for n, s in self.schemas.items()]
        return code.class_file.format(
            namespace=f"{cs.to_pascal(self.title)}Client",
            classes="\n".join(
                code.data_class.format(
                    name=m.name,
                    doc=m.doc,
                    fields=f"\n{self._indent * 2}".join(m.fields),
                )
                for m in models
            ),
        ).lstrip()

    def _get_cs_type(self, schema: SchemaObject) -> str:
        if schema is None:
            return "object"

        if schema.type:
            if schema.type == "array":
                return f"List<{self._get_cs_type(schema.items)}>"
            elif schema.type == "object":
                return "Dictionary<string, object>"
            elif isinstance(schema.type, list):
                # FIXME C# unions?.
                return "object"
            return self._type_map[schema.type]
        elif schema_list := schema.all_of or schema.any_of or schema.one_of:
            # FIXME C# unions?.
            return "object"
        elif schema.ref:
            return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

        return "object"
