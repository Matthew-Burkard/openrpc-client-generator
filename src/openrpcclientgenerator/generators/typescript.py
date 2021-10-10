import re
from dataclasses import dataclass, field

from openrpc.objects import MethodObject, SchemaObject

from openrpcclientgenerator import util
from openrpcclientgenerator.templates.typescript import code


@dataclass
class _Model:
    name: str
    args: list[str] = field(default_factory=lambda: [])
    fields: list[str] = field(default_factory=lambda: [])
    property_names: dict[str, str] = field(default_factory=lambda: {})


class TypeScriptGenerator:
    def __init__(
        self, title: str, methods: list[MethodObject], schemas: dict[str, SchemaObject]
    ) -> None:
        self.title = title
        self.methods = methods
        self.schemas = schemas
        self._type_map = {
            "integer": "number",
            "number": "number",
            "boolean": "boolean",
            "string": "string",
            "null": None,
        }

    def get_methods(self) -> str:
        def get_type(schema: SchemaObject) -> str:
            # Get TypeScript type from JSON Schema type.
            if schema.type:
                if schema.type == "array":
                    return_type = f"{get_type(schema.items)}[]"
                elif schema.type == "object":
                    v_type = get_type(schema.items) if schema.items else "any"
                    return_type = f"HashMap<string, {v_type}>"
                else:
                    return_type = self._type_map[schema.type]
            elif schema.any_of:
                return_type = "|".join(
                    t for s in schema.any_of if (t := get_type(s)) is not None
                )
            # TODO all_of, one_of
            else:
                return_type = schema.ref.removeprefix("#/components/schemas/")
                return_type = f"m.{return_type}"
            return return_type

        def get_method(method: MethodObject) -> str:
            return_type = get_type(method.result.json_schema)
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
                p_name = util.to_camel_case(p.name)
                args.append(f"{p_name}{required}: {get_type(p.json_schema)}")
            return code.method.format(
                name=util.to_camel_case(re.sub(r".*?\.", "", method.name)),
                args=", ".join(args),
                return_type=return_type,
                params=", ".join(util.to_camel_case(p.name) for p in method.params),
                method=method.name,
                result_casting=result_cast,
            )

        return code.client.format(
            name=util.to_pascal_case(self.title),
            methods="".join(get_method(method) for method in self.methods),
        ).lstrip()

    def get_models(self) -> str:
        indent = " " * 2
        models = [
            self._get_model(name, schema) for name, schema in self.schemas.items()
        ]
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

    def _get_model(self, name: str, schema: SchemaObject) -> _Model:
        def _get_type(s: SchemaObject) -> str:
            if s.type == "array":
                return f"{_get_type(s.items)}[]"
            if s.type:
                return self._type_map[s.type]
            else:
                return s.ref.removeprefix("#/components/schemas/")

        model = _Model(name)
        for prop_name, prop in schema.properties.items():
            required = "?" if prop_name in (schema.required or []) else ""
            field_type = _get_type(prop)
            ts_name = util.to_camel_case(prop_name)
            model.property_names[ts_name] = prop_name
            model.fields.append(f"{ts_name}{required}: {field_type};")
            model.args.append(f"{ts_name}?: {field_type}")

        model.fields.sort(key=lambda x: bool(re.search(r"[^:]+\?:", x)))
        return model
