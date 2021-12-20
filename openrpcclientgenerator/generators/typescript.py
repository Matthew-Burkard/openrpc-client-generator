"""Provides a TypeScript RPC client generator."""
import re
from dataclasses import dataclass, field

import caseswitcher as cs
from openrpc.objects import MethodObject, OpenRPCObject, ParamStructure, SchemaObject

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
            "object": "object",
        }
        self._indent = " " * 2
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
            servers=f"\n{self._indent}".join(
                [f"{k} = '{v}'," for k, v in self._get_servers().items()]
            ),
        ).lstrip()

    def _get_methods(self) -> str:
        def _get_method(method: MethodObject) -> str:
            def _get_type(schema: SchemaObject) -> str:
                ts_type = self._get_ts_type(schema)
                return f"m.{ts_type}" if self._is_model(ts_type) else ts_type

            def _get_array_params() -> str:
                array_params = ", ".join(cs.to_camel(it.name) for it in method.params)
                return f"serializeArrayParams([{array_params}])"

            def _get_object_params() -> str:
                key_value_pairs = ", ".join(
                    f"'{it.name}': {cs.to_camel(it.name)}" for it in method.params
                )
                return f"serializeObjectParams({{{key_value_pairs}}})"

            return_type = _get_type(method.result.json_schema)
            return_value = f"result as {return_type}"
            # If not a primitive return type.
            if self._is_model(return_type):
                if return_type.endswith("[]"):
                    result_origin = return_type.removesuffix("[]")
                    return_value = f"result.map(it => {result_origin}.fromJSON(it))"
                else:
                    return_value = f"{return_type}.fromJSON(result)"

            # Get method arguments.
            args = []
            for p in method.params:
                required = "" if p.required else "?"
                p_name = cs.to_camel(p.name)
                args.append(f"{p_name}{required}: {_get_type(p.json_schema)}")

            # Get method call params.
            if method.param_structure == ParamStructure.BY_NAME:
                params = _get_object_params()
            else:
                params = _get_array_params()

            return code.method.format(
                name=cs.to_camel(method.name),
                args=", ".join(args),
                return_type=return_type,
                params=params,
                method=method.name,
                return_value=return_value,
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

        models = [_get_model(n, s) for n, s in self.schemas.items()]
        models = "\n".join(
            code.data_class.format(
                name=model.name,
                fields=self._indent + f"\n{self._indent}".join(model.fields),
                args=", ".join(model.args),
                initiations="\n".join(
                    f"{self._indent * 2}this.{name} = {name};"
                    for name in model.property_names.keys()
                ),
                to_json="\n".join(
                    f"{self._indent * 3}{prop_name}: toJSON(this.{name}),"
                    for name, prop_name in model.property_names.items()
                ),
                from_json="\n".join(
                    f"{self._indent * 2}instance.{name} = fromJSON(data.{prop_name});"
                    for name, prop_name in model.property_names.items()
                ),
            )
            for model in models
        )
        return code.models_file.format(models=models)

    def _get_ts_type(self, schema: SchemaObject) -> str:
        # Get TypeScript type from JSON Schema type.
        if schema is None:
            return "any"

        if schema.type:
            if schema.type == "array":
                return f"{self._get_ts_type(schema.items)}[]"
            elif schema.type == "object":
                return "object"
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

    def _is_model(self, string: str) -> bool:
        return not ((string in self._type_map.values()) or string == "any")
