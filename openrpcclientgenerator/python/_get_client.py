"""Provides a Python RPC client generator."""
from dataclasses import dataclass

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, ParamStructure, SchemaObject

from openrpcclientgenerator.common import get_servers
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.python._common import get_py_type, indent
from openrpcclientgenerator.python import _templates


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


def get_client(
    openrpc: OpenRPCObject,
    schemas: dict[str, SchemaObject],
    transport: Transport = Transport.HTTP,
) -> str:
    """Get a Python RPC client file content."""
    models_import = "from .models import *" if schemas else ""
    return _templates.client_file.format(
        models_import=models_import,
        transport=transport.value,
        title=cs.to_pascal(openrpc.info.title),
        async_methods=_get_methods(openrpc.methods, is_async=True),
        methods=_get_methods(openrpc.methods, is_async=False),
        servers=f"\n{indent}".join(
            [f'{k} = "{v}"' for k, v in get_servers(openrpc.servers).items()]
        ),
    )


def _get_methods(methods: list[MethodObject], *_args, is_async: bool = True) -> str:
    return "".join(_get_method(m, is_async=is_async) for m in methods)


def _get_method(method: MethodObject, *_args, is_async: bool = True) -> str:
    def _get_list_params() -> str:
        return f"[{', '.join(cs.to_snake(it.name) for it in method.params)}]"

    def _get_dict_params() -> str:
        key_value_pairs = ",".join(
            f'"{it.name}": {cs.to_snake(it.name)}' for it in method.params
        )
        return f"{{{key_value_pairs}}}"

    # Get method arguments.
    args = []
    for param in method.params:
        p_type = get_py_type(param.schema_)
        if not param.required and not p_type.startswith("Optional"):
            p_type = f"Optional[{p_type}]"
        if p_type.startswith("Optional"):
            p_type += " = None"
        args.append(f", {cs.to_snake(param.name)}: {p_type}")
    args.sort(key=lambda x: str(x).find("Optional") != -1)

    # Get method call params.
    if method.param_structure == ParamStructure.BY_NAME:
        params = _get_dict_params()
    else:
        params = _get_list_params()

    # Get return type and add code to deserialize results.
    return_type = get_py_type(method.result.schema_)

    # Get doc string.
    doc = f'\n{indent * 2}"""{method.description}"""' if method.description else ""

    template = _templates.async_method if is_async else _templates.method
    return template.format(
        name=cs.to_snake(method.name),
        method=method.name,
        args="self" + "".join(args),
        return_type=return_type,
        doc=doc,
        params=params,
    )
