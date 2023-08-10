"""Provides a C# RPC client generator."""
import re
from dataclasses import dataclass

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, SchemaObject

from openrpcclientgenerator.generators._generator import CodeGenerator
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.templates.dotnet import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


class CSharpCodeGenerator(CodeGenerator):
    """Class to generate the code for a C# RPC Client."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        """Init generator for C# code.

        :param openrpc: OpenRPC API object to generate client for.
        :param schemas: JSON Schema schemas.
        """
        self._type_map = {
            "boolean": "bool",
            "integer": "int",
            "number": "double",
            "string": "string",
            "null": "null",
            "object": "object",
        }
        self._indent = " " * 4
        super(CSharpCodeGenerator, self).__init__(openrpc, schemas)

    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get a C# RPC client.

        :param transport: Transport method of the client.
        :return: C# class with all RPC methods.
        """
        return code.client_file.format(
            namespace=f"{cs.to_pascal(self.openrpc.info.title)}Client",
            title=cs.to_pascal(self.openrpc.info.title),
            transport=transport.value.capitalize(),
            methods=self._get_methods(),
        ).lstrip()

    def _get_methods(self) -> str:
        def _get_method(method: MethodObject) -> str:
            if len(method.params) > 1:
                params = ", ".join(cs.to_camel(it.name) for it in method.params)
                params = f", new List<object> {{new List<object> {{{params}}}}}"
            else:
                # Length is 1 or 0.
                params = "".join(cs.to_camel(it.name) for it in method.params)
                if len(method.params) > 0:
                    params = ", " + f"new List<object> {{{params}}}"

            if method.description:
                doc = f"\n{self._indent * 2}".join(
                    f" * {line.strip()}".rstrip()
                    for line in method.description.split("\n")
                )
            else:
                doc = " * No description provided."
            return_type = self._get_cs_type(method.result.schema_)
            args = ", ".join(
                f"{self._get_cs_type(it.schema_)} {cs.to_camel(it.name)}"
                for it in method.params
            )
            name = cs.to_pascal(re.sub(r".*?\.", "", method.name))
            if return_type == "null":
                return code.void_method.format(
                    doc=doc, name=name, args=args, method=method.name, params=params
                )
            return code.method.format(
                doc=doc,
                return_type=return_type,
                name=name,
                args=args,
                method=method.name,
                params=params,
            )

        return "\n".join(_get_method(m) for m in self.openrpc.methods)

    def get_models(self) -> str:
        """Get C# code of all Model declarations."""

        def _get_model(name: str, schema: SchemaObject) -> _Model:
            fields = []
            if schema.properties:
                for prop_name, prop in schema.properties.items():
                    c_sharp_type = self._get_cs_type(prop)

                    if prop_name in (schema.required or []):
                        required = ", Required = Required.Always"
                    else:
                        required = ""
                        if c_sharp_type in ["int", "double", "bool"]:
                            c_sharp_type = f"{c_sharp_type}?"

                    field_name = cs.to_pascal(prop_name)
                    if field_name == name:
                        field_name = f"Sub{field_name}"
                    if "default" not in prop.model_fields_set:
                        default = ""
                    elif prop.default in [True, False, None]:
                        default_value = {
                            True: "true",
                            False: "false",
                            None: "null",
                        }.get(prop.default) or prop.default
                        default = f"[DefaultValue({default_value})]"
                    else:
                        default = ""
                    fields.append(
                        code.field.format(
                            prop_name=prop_name,
                            req=required,
                            default=default,
                            type=c_sharp_type,
                            name=field_name,
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

        models = [_get_model(n, s) for n, s in self.schemas.items()]
        return code.class_file.format(
            namespace=f"{cs.to_pascal(self.openrpc.info.title)}Client",
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

        type_ = "object"
        if schema.type:
            if schema.type == "array":
                type_ = f"List<{self._get_cs_type(schema.items)}>"
            elif schema.type == "object":
                type_ = "Dictionary<string, object>"
            elif isinstance(schema.type, list):
                type_ = "object"
            elif schema.type == "string" and schema.format:
                type_ = {"binary": "byte[]"}.get(schema.format) or "string"
            else:
                type_ = self._type_map[schema.type]
        elif schema.all_of or schema.any_of or schema.one_of:
            type_ = "object"
        elif schema.ref:
            type_ = re.sub(r"#/.*/(.*)", r"\1", schema.ref)

        return type_
