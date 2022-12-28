"""Provides a Python RPC client generator."""
import re
from dataclasses import dataclass

import caseswitcher as cs
from openrpc import MethodObject, OpenRPCObject, ParamStructure, SchemaObject

from openrpcclientgenerator.generators._generator import CodeGenerator
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.templates.python import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


class PythonCodeGenerator(CodeGenerator):
    """Class to generate the code for a Python RPC Client."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        """Instantiate PythonCodeGenerator class.

        :param openrpc: OpenRPC doc to generate code from.
        :param schemas: Schemas used.
        """
        self._type_map = {
            "boolean": "bool",
            "integer": "int",
            "number": "float",
            "string": "str",
            "null": "None",
            "object": "dict[str, Any]",
        }
        self._indent = " " * 4
        self._import_field = False
        super(PythonCodeGenerator, self).__init__(openrpc, schemas)

    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get a Python RPC client.

        :param transport: Transport method of the client.
        :return: Python class with all RPC methods.
        """
        models_import = "from .models import *" if self.schemas else ""
        return code.client_file.format(
            models_import=models_import,
            transport=transport.value,
            title=cs.to_pascal(self.openrpc.info.title),
            async_methods=self._get_methods(),
            methods=self._get_methods(is_async=False),
            servers=f"\n{self._indent}".join(
                [f'{k} = "{v}"' for k, v in self._get_servers().items()]
            ),
        )

    def _get_methods(self, is_async: bool = True) -> str:
        def _get_method(method: MethodObject) -> str:
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
                p_type = self._get_py_type_from_schema(param.schema_)
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
            return_type = self._get_py_type_from_schema(method.result.schema_)

            # Get doc string.
            if method.description:
                doc = f'\n{self._indent * 2}"""{method.description}"""'
            else:
                doc = ""

            template = code.async_method if is_async else code.method
            return template.format(
                name=cs.to_snake(method.name),
                method=method.name,
                args="self" + "".join(args),
                return_type=return_type,
                doc=doc,
                params=params,
            )

        return "".join(_get_method(m) for m in self.openrpc.methods)

    def get_models(self) -> str:
        """Get Python code of all Model declarations."""
        _all = []

        def _get_model(name: str, schema: SchemaObject) -> _Model:
            fields = []
            if schema.properties:
                for n, prop in schema.properties.items():
                    field_name = cs.to_snake(n)
                    needs_alias = field_name != n
                    required = n in (schema.required or [])
                    if needs_alias and required:
                        default = f' = Field(alias="{n}")'
                        self._import_field = True
                    elif needs_alias:
                        default = f' = Field(None, alias="{n}")'
                        self._import_field = True
                    else:
                        default = " = None"
                    fields.append(
                        code.field.format(
                            name=field_name,
                            type=self._get_py_type_from_schema(prop),
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

            fields.sort(key=lambda x: x.endswith(" = None") or "Field(None" in x)
            fields = [
                re.sub(r": (.*?) =", r": Optional[\1] =", field)
                if field.endswith(" = None")
                else field
                for field in fields
            ]
            _all.append(name)
            return _Model(
                name=name,
                doc=f'"""{doc}"""',
                fields=fields,
            )

        models = [_get_model(n, s) for n, s in self.schemas.items()]
        return code.model_file.format(
            field_import=", Field" if self._import_field else "",
            all=", ".join(f'"{it}"' for it in _all),
            classes="\n".join(
                code.data_class.format(
                    name=model.name,
                    doc=model.doc,
                    fields=f"\n{self._indent}".join(model.fields),
                )
                for model in models
            ),
            update_refs="\n".join(f"{m.name}.update_forward_refs()" for m in models),
        )

    def _get_py_type_from_schema(self, schema: SchemaObject) -> str:
        # Get Python type from JSON Schema type.

        def _get_union_type_from_strings(types: list[str]) -> str:
            if len(types) == 2 and "null" in types:
                types.remove("null")
                return f"Optional[{self._type_map[types[0]]}]"
            if "null" in types:
                types.remove("null")
                type_str = ", ".join(self._type_map[it] for it in types)
                return f"Optional[Union[{type_str}]]"
            return f"Union[{', '.join(self._type_map[it] for it in types)}]"

        def _get_union_type_from_schemas(types: list[SchemaObject]) -> str:
            str_types = [self._get_py_type_from_schema(it) for it in types]
            if len(str_types) == 2 and "None" in str_types:
                str_types.remove("None")
                return f"Optional[{str_types[0]}]"
            if "None" in str_types:
                str_types.remove("None")
                return f"Optional[Union[{', '.join(str_types)}]]"
            return f"Union[{', '.join(str_types)}]"

        if schema is None:
            return "Any"

        if schema.type:
            if schema.type == "array":
                return f"list[{self._get_py_type_from_schema(schema.items)}]"
            elif schema.type == "object":
                v_type = (
                    self._get_py_type_from_schema(schema.items)
                    if schema.items
                    else "Any"
                )
                return f"dict[str, {v_type}]"
            elif isinstance(schema.type, list):
                return _get_union_type_from_strings(schema.type)
            if schema.type == "string" and schema.format:
                return {"binary": "bytes"}.get(schema.format) or "str"
            return self._type_map[schema.type]
        elif schema_list := schema.all_of or schema.any_of or schema.one_of:
            return _get_union_type_from_schemas(schema_list)
        elif schema.ref:
            return re.sub(r"#/.*/(.*)", r"\1", schema.ref)

        return "Any"
