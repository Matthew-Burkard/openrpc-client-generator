"""Provides a Kotlin RPC client generator."""
import re
from dataclasses import dataclass, field

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, SchemaObject

from openrpcclientgenerator.generators._generator import CodeGenerator
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.templates.kotlin import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str] = field(default_factory=lambda: [])


class KotlinCodeGenerator(CodeGenerator):
    """Class to generate the code for a Kotlin RPC Client."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        """Instantiate KotlinCodeGenerator class.

        :param openrpc: OpenRPC doc to generate code from.
        :param schemas: Schemas used.
        """
        self._type_map = {
            "boolean": "Boolean",
            "integer": "Int",
            "number": "Double",
            "string": "String",
            "null": "null",
            "object": "Map<String, Any>",
        }
        self._indent = " " * 2
        super(KotlinCodeGenerator, self).__init__(openrpc, schemas)

    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get a Kotlin RPC client.

        :param transport: Transport method of the client.
        :return: Python class with all RPC methods.
        """
        return code.client_file.format(
            title=cs.to_pascal(self.openrpc.info.title),
            transport=transport.value,
            methods=self._get_methods(),
        )

    def _get_methods(self) -> str:
        def _get_method(method: MethodObject) -> str:
            args = []
            for param in method.params:
                k_type = self._get_kotlin_type(param.schema_)
                if not param.required:
                    k_type = f"{k_type}?"
                args.append(f"{cs.to_camel(param.name)}: {k_type}")

            if len(method.params) > 1:
                params = ", ".join(cs.to_camel(it.name) for it in method.params)
            else:
                # Length is 1 or 0.
                params = "".join(cs.to_camel(it.name) for it in method.params)

            return code.method.format(
                doc=method.description,
                name=cs.to_camel(re.sub(r".*?\.", "", method.name)),
                args=", ".join(args),
                return_type=self._get_kotlin_type(method.result.schema_),
                params=params,
            )

        return "".join(_get_method(m) for m in self.openrpc.methods).lstrip()

    def get_models(self) -> str:
        """Get Kotlin code of all model declarations."""

        def _get_model(name: str, schema: SchemaObject) -> _Model:
            fields = []
            if schema.properties:
                for n, prop in schema.properties.items():
                    required = n in (schema.required or [])
                    fields.append(
                        code.field.format(
                            name=cs.to_camel(n),
                            type=self._get_kotlin_type(prop) + "?" if required else "",
                            default=" = null" if required else "",
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
            return _Model(name, doc, fields)

        models = [_get_model(n, s) for n, s in self.schemas.items()]
        return code.model_file.format(
            classes="\n".join(
                code.model.format(
                    name=model.name,
                    doc=model.doc,
                    fields=f"\n{self._indent}".join(model.fields),
                )
                for model in models
            )
        )

    def _get_kotlin_type(self, schema: SchemaObject) -> str:
        # Get Kotlin type from JSON Schema type.
        if schema.type:
            if schema.type == "array":
                return f"List<{self._get_kotlin_type(schema.items)}>"
            if schema.type == "object":
                v_type = self._get_kotlin_type(schema.items) if schema.items else "Any"
                return f"Map<String, {v_type}>"
            if isinstance(schema.type, list):
                types = " | ".join(self._type_map[it] for it in schema.type)
                return f"dynamic /* {types} */"
            # TODO Class with ByteArray should override equals and hashCode.
            if schema.type == "string" and schema.format:
                return {"binary": "ByteArray"}.get(schema.format) or "String"
            return self._type_map[schema.type]
        if schema_list := schema.all_of or schema.any_of or schema.one_of:
            types = " | ".join(self._get_kotlin_type(it) for it in schema_list)
            return f"dynamic /* {types} */"
        if schema.ref:
            return re.sub(r"#/.*/(.*)", r"\1", schema.ref)
        return "Any"
