"""Functions shared across the project."""
from openrpc import SchemaObject


def get_schemas(schemas: dict[str, SchemaObject]) -> dict[str, SchemaObject]:
    """Recursively get all schemas from a dict schemas.

    :param schemas: The schemas to recursively search for sub-schemas.
    :return: All schemas with their names as keys.
    """
    schemas = schemas or {}
    for _name, schema in schemas.items():
        if schema.definitions:
            schemas = {**schemas, **get_schemas(schema.definitions)}
    return schemas
