"""TypeScript RPC client generate related functions."""
__all__ = ("get_models",)

import re
from dataclasses import dataclass, field

import caseswitcher as cs
from openrpc import SchemaObject

from openrpcclientgenerator.templates.typescript import code
from openrpcclientgenerator.typescript._common import get_ts_type, indent


@dataclass
class _Model:
    name: str
    args: list[str] = field(default_factory=lambda: [])
    fields: list[str] = field(default_factory=lambda: [])
    property_names: dict[str, str] = field(default_factory=lambda: {})


def get_models(schemas: dict[str, SchemaObject]) -> str:
    """Get TypeScript models."""

    def _get_model(name: str, schema: SchemaObject) -> _Model:
        model = _Model(name)
        schema.properties = schema.properties or {}
        for prop_name, prop in schema.properties.items():
            required = "?" if prop_name in (schema.required or []) else ""
            field_type = get_ts_type(prop)
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
