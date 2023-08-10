"""Provides a Python RPC client generator."""
import re
from dataclasses import dataclass

import caseswitcher as cs
from openrpc import SchemaObject

from openrpcclientgenerator.python._common import get_py_type_from_schema, indent
from openrpcclientgenerator.templates.python import code


@dataclass
class _Model:
    name: str
    doc: str
    fields: list[str]


def get_models(schemas: dict[str, SchemaObject]) -> str:
    """Get Python code of all Model declarations."""
    _all = []
    # Does Pydantic `Field` need to be imported?
    import_field = False

    def _get_model(name: str, schema: SchemaObject) -> _Model:
        nonlocal import_field
        fields = []
        if schema.properties:
            for n, prop in schema.properties.items():
                field_name = cs.to_snake(n)
                needs_alias = field_name != n
                required = n in (schema.required or [])
                if needs_alias and required:
                    default = f' = Field(alias="{n}")'
                    import_field = True
                elif needs_alias:
                    default = f' = Field(None, alias="{n}")'
                    import_field = True
                else:
                    default = " = None"
                fields.append(
                    code.field.format(
                        name=field_name,
                        type=get_py_type_from_schema(prop),
                        default=default,
                    )
                )
        if schema.description:
            doc = f"\n{indent}".join(
                line.strip() for line in schema.description.split("\n")
            )
            # Remove trailing spaces from blank lines.
            doc = "\n".join(line.rstrip() for line in doc.split("\n"))
        else:
            doc = f"{schema.title} object."
        if len(doc.split("\n")) > 1:
            doc += indent

        fields.sort(key=lambda x: x.endswith(" = None") or "Field(None" in x)
        fields = [
            re.sub(r": (.*?) =", r": Optional[\1] =", field)
            if field.endswith(" = None")
            else field
            for field in fields
        ]
        _all.append(name)
        return _Model(name=name, doc=f'"""{doc}"""', fields=fields)

    models = [_get_model(n, s) for n, s in schemas.items()]
    return code.model_file.format(
        field_import=", Field" if import_field else "",
        all=", ".join(f'"{it}"' for it in _all),
        classes="\n".join(
            code.data_class.format(
                name=model.name, doc=model.doc, fields=f"\n{indent}".join(model.fields)
            )
            for model in models
        ),
        update_refs="\n".join(f"{m.name}.update_forward_refs()" for m in models),
    )
