from openrpc.objects import SchemaObject


def get_schemas(schemas: dict[str, SchemaObject]) -> dict[str, SchemaObject]:
    schemas = schemas or {}
    for name, schema in schemas.items():
        if schema.definitions:
            schemas = {**schemas, **get_schemas(schema.definitions)}
    return schemas
