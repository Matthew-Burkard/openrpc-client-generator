"""TypeScript RPC client generate related functions."""
__all__ = ("get_client",)

import re
from dataclasses import dataclass, field

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, ParamStructure, SchemaObject

from openrpcclientgenerator.generators._common import _get_servers
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.templates.typescript import code

type_map = {
    "boolean": "boolean",
    "integer": "number",
    "number": "number",
    "string": "string",
    "null": "null",
    "object": "object",
}
indent = " " * 2


@dataclass
class _Model:
    name: str
    args: list[str] = field(default_factory=lambda: [])
    fields: list[str] = field(default_factory=lambda: [])
    property_names: dict[str, str] = field(default_factory=lambda: {})


def get_client(
    openrpc: OpenRPCObject,
    schemas: dict[str, SchemaObject],
    transport: Transport = Transport.HTTP,
) -> str:
    """Generate a TypeScript RPC client."""
    # Get all models used in methods.
    used_models = [
        _get_ts_type(p.schema_) for m in openrpc.methods for p in m.params + [m.result]
    ]
    used_models.sort()

    # If there are schemas, add imports for them if they are used.
    if schemas:
        models = ", ".join(k for k in schemas.keys() if k in used_models)
        models_import = f"import {{{models}}} from './models.js';"
    else:
        models_import = ""

    return code.client.format(
        models_import=models_import,
        name=cs.to_pascal(openrpc.info.title),
        methods="".join(_get_method(m) for m in openrpc.methods),
        transport=transport.value,
        servers=f"\n{indent}".join(
            [f"{k} = '{v}'," for k, v in _get_servers(openrpc.servers).items()]
        ),
        parameter_interfaces=_get_parameter_interfaces(openrpc.methods),
    ).lstrip()


def get_models(schemas: dict[str, SchemaObject]) -> str:
    """Get TypeScript models."""

    def _get_model(name: str, schema: SchemaObject) -> _Model:
        model = _Model(name)
        schema.properties = schema.properties or {}
        for prop_name, prop in schema.properties.items():
            required = "?" if prop_name in (schema.required or []) else ""
            field_type = _get_ts_type(prop)
            ts_name = cs.to_camel(prop_name)
            model.property_names[ts_name] = prop_name
            model.fields.append(f"{ts_name}{required}: {field_type};")
            model.args.append(f"{ts_name}?: {field_type}")

        model.fields.sort(key=lambda x: bool(re.search(r"[^:]+\?:", x)))
        return model

    models = [_get_model(n, s) for n, s in schemas.items()]
    models_str = "\n".join(
        code.data_class.format(
            name=model.name,
            fields=indent + f"\n{indent}".join(model.fields),
            args=", ".join(model.args),
            initiations="\n".join(
                f"{indent * 2}this.{name} = {name};"
                for name in model.property_names.keys()
            ),
            to_json="\n".join(
                f"{indent * 3}{prop_name}: toJSON(this.{name}),"
                for name, prop_name in model.property_names.items()
            ),
            from_json="\n".join(
                f"{indent * 2}instance.{name} = fromJSON(data.{prop_name});"
                for name, prop_name in model.property_names.items()
            ),
        )
        for model in models
    )
    return code.models_file.format(models=models_str)


def _get_method(method: MethodObject) -> str:
    def _get_array_args() -> str:
        array = []
        for p in method.params:
            required = "" if p.required else "?"
            p_name = cs.to_camel(p.name)
            array.append(f"{p_name}{required}: {_get_ts_type(p.schema_)}")
        return ", ".join(array)

    def _get_object_args() -> str:
        default = " = {}" if all(not p.required for p in method.params) else ""
        args_str = ", ".join(cs.to_camel(p.name) for p in method.params)
        return f"{{{args_str}}}: {cs.to_pascal(method.name)}Parameters{default}"

    def _get_array_params() -> str:
        array_params = ", ".join(cs.to_camel(it.name) for it in method.params)
        return f"serializeArrayParams([{array_params}])"

    def _get_object_params() -> str:
        key_value_pairs = ", ".join(
            f"'{it.name}': {cs.to_camel(it.name)}" for it in method.params
        )
        return f"serializeObjectParams({{{key_value_pairs}}})"

    # Get return type.
    return_type = _get_ts_type(method.result.schema_)
    return_value = f"result as {return_type}"
    is_model = not (return_type in type_map.values() or return_type == "any")
    # If not a primitive return type.
    if is_model:
        if return_type.endswith("[]"):
            result_origin = return_type.removesuffix("[]")
            return_value = f"result.map(it => {result_origin}.fromJSON(it))"
        else:
            return_value = f"{return_type}.fromJSON(result)"

    # Get function args and method call params.
    if method.param_structure == ParamStructure.BY_NAME:
        args = _get_object_args()
        params = _get_object_params()
    else:
        args = _get_array_args()
        params = _get_array_params()

    return code.method.format(
        name=cs.to_camel(method.name),
        args=args,
        return_type=return_type,
        params=params,
        method=method.name,
        return_value=return_value,
    )


def _get_parameter_interfaces(methods: list[MethodObject]) -> str:
    interfaces = []
    for method in methods:
        if method.param_structure != ParamStructure.BY_NAME:
            continue
        interface_args = []
        for p in method.params:
            required = "" if p.required else "?"
            p_name = cs.to_camel(p.name)
            interface_args.append(f"{p_name}{required}: {_get_ts_type(p.schema_)}")
        args_str = f",\n{indent}".join(interface_args)
        interface_name = f"interface {cs.to_pascal(method.name)}Parameters"
        interfaces.append(f"{interface_name} {{\n{indent}{args_str}\n}}")

    if interfaces:
        return "\n\n" + "\n\n\n".join(interfaces)
    return ""


def _get_ts_type(schema: SchemaObject) -> str:
    # Get TypeScript type from JSON Schema type.
    if schema is None:
        return "any"

    if schema.type:
        if schema.type == "array":
            return f"{_get_ts_type(schema.items)}[]"
        elif schema.type == "object":
            return "object"
        elif isinstance(schema.type, list):
            return " | ".join(type_map[it] for it in schema.type)
        if schema.type == "string" and schema.format:
            return {"binary": "any"}.get(schema.format) or "string"
        return type_map[schema.type]
    elif schema_list := schema.all_of or schema.any_of or schema.one_of:
        return " | ".join(_get_ts_type(it) for it in schema_list)
    elif schema.ref:
        return re.sub(r"#/.*/(.*)", r"\1", schema.ref)
    return "any"
