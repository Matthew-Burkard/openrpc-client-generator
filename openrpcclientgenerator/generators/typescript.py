"""Provides a TypeScript RPC client generator."""
import re
from dataclasses import dataclass, field

import caseswitcher as cs
from openrpc.objects import MethodObject, OpenRPCObject, SchemaObject

from openrpcclientgenerator.generators._generator import CodeGenerator
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.templates.typescript import code


@dataclass
class _Model:
    name: str
    args: list[str] = field(default_factory=lambda: [])
    fields: list[str] = field(default_factory=lambda: [])
    property_names: dict[str, str] = field(default_factory=lambda: {})


class TypeScriptGenerator(CodeGenerator):
    """Class to generate the code for a TypeScript RPC Client."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        self._type_map = {
            "boolean": "boolean",
            "integer": "number",
            "number": "number",
            "string": "string",
            "null": "null",
            "object": "Map<string, any>",
        }
        super(TypeScriptGenerator, self).__init__(openrpc, schemas)

    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get a TypeScript RPC client.

        :param transport: Transport method of the client.
        :return: TypeScript class with all RPC methods.
        """
        return code.client.format(
            name=cs.to_pascal(self.openrpc.info.title),
            methods=self._get_methods(),
            transport=transport.value,
        ).lstrip()

    def _get_methods(self) -> str:
        def _get_type(schema: SchemaObject) -> str:
            ts_type = self._get_ts_type(schema)
            return ts_type if ts_type in self._type_map.values() else f"m.{ts_type}"

        def _get_method(method: MethodObject) -> str:
            return_type = _get_type(method.result.json_schema)
            if return_type in self._type_map.values():
                result_cast = f"result = result as {return_type}"
            else:
                template = (
                    code.array_from_json
                    if return_type.endswith("[]")
                    else code.from_json
                )
                result_cast = template.format(
                    return_type=return_type.removesuffix("[]")
                ).strip()
            args = []
            for p in method.params:
                required = "" if p.required else "?"
                p_name = cs.to_camel(p.name)
                args.append(f"{p_name}{required}: {_get_type(p.json_schema)}")
            return code.method.format(
                name=cs.to_camel(method.name),
                args=", ".join(args),
                return_type=return_type,
                params=", ".join(cs.to_camel(p.name) for p in method.params),
                method=method.name,
                result_casting=result_cast,
            )

        return "".join(_get_method(method) for method in self.openrpc.methods)

    def get_models(self) -> str:
        """Get TypeScript code of all Model declarations."""

        def _get_model(name: str, schema: SchemaObject) -> _Model:
            model = _Model(name)
            for prop_name, prop in schema.properties.items():
                required = "?" if prop_name in (schema.required or []) else ""
                field_type = self._get_ts_type(prop)
                ts_name = cs.to_camel(prop_name)
                model.property_names[ts_name] = prop_name
                model.fields.append(f"{ts_name}{required}: {field_type};")
                model.args.append(f"{ts_name}?: {field_type}")

            model.fields.sort(key=lambda x: bool(re.search(r"[^:]+\?:", x)))
            return model

        indent = " " * 2
        models = [_get_model(n, s) for n, s in self.schemas.items()]
        return "\n".join(
            code.data_class.format(
                name=model.name,
                fields=indent + f"\n{indent}".join(model.fields),
                args=", ".join(model.args),
                initiations="\n".join(
                    f"{indent * 2}this.{name} = {name};"
                    for name in model.property_names.keys()
                ),
                to_json="\n".join(
                    f"{indent * 3}{prop_name}: this.{name},"
                    for name, prop_name in model.property_names.items()
                ),
                from_json="\n".join(
                    f"{indent * 3}instance.{name} = data.{prop_name};"
                    for name, prop_name in model.property_names.items()
                ),
            )
            for model in models
        )

    def _get_ts_type(self, schema: SchemaObject) -> str:
        # Get TypeScript type from JSON Schema type.
        if schema is None:
            return "any"

        if schema.type:
            if schema.type == "array":
                return f"{self._get_ts_type(schema.items)}[]"
            elif schema.type == "object":
                v_type = self._get_ts_type(schema.items) if schema.items else "any"
                return f"Map<string, {v_type}>"
            elif isinstance(schema.type, list):
                return " | ".join(self._type_map[it] for it in schema.type)
            if schema.type == "string" and schema.format:
                return {"binary": "any"}.get(schema.format) or "string"
            return self._type_map[schema.type]
        elif schema_list := schema.all_of or schema.any_of or schema.one_of:
            return " | ".join(self._get_ts_type(it) for it in schema_list)
        elif schema.ref:
            return re.sub(r"#/.*/(.*)", r"\1", schema.ref)
        return "any"
