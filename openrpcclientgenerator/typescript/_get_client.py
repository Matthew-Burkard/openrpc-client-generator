"""TypeScript RPC client generate related functions."""
__all__ = ("get_client",)

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, ParamStructure, SchemaObject

from openrpcclientgenerator.common import get_servers
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.typescript import _templates
from openrpcclientgenerator.typescript._common import get_ts_type, indent, type_map


def get_client(
    openrpc: OpenRPCObject,
    schemas: dict[str, SchemaObject],
    transport: Transport = Transport.HTTP,
) -> str:
    """Get a TypeScript RPC client file content."""
    # Get all models used in methods.
    used_models = [
        get_ts_type(p.schema_) for m in openrpc.methods for p in m.params + [m.result]
    ]
    used_models.sort()

    # If there are schemas, add imports for them if they are used.
    if schemas:
        models = ", ".join(k for k in schemas.keys() if k in used_models)
        models_import = f"import {{{models}}} from './models.js';"
    else:
        models_import = ""

    return _templates.client.format(
        models_import=models_import,
        name=cs.to_pascal(openrpc.info.title),
        methods="".join(_get_method(m) for m in openrpc.methods),
        transport=transport.value,
        servers=f"\n{indent}".join(
            [f"{k} = '{v}'," for k, v in get_servers(openrpc.servers).items()]
        ),
        parameter_interfaces=_get_parameter_interfaces(openrpc.methods),
    ).lstrip()


def _get_method(method: MethodObject) -> str:
    def _get_array_args() -> str:
        array = []
        for p in method.params:
            required = "" if p.required else "?"
            p_name = cs.to_camel(p.name)
            array.append(f"{p_name}{required}: {get_ts_type(p.schema_)}")
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
    return_type = get_ts_type(method.result.schema_)
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

    return _templates.method.format(
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
            interface_args.append(f"{p_name}{required}: {get_ts_type(p.schema_)}")
        args_str = f",\n{indent}".join(interface_args)
        interface_name = f"interface {cs.to_pascal(method.name)}Parameters"
        interfaces.append(f"{interface_name} {{\n{indent}{args_str}\n}}")

    if interfaces:
        return "\n\n" + "\n\n\n".join(interfaces)
    return ""
