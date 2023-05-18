"""Functions shared across the project."""
import os
import subprocess
import uuid
from pathlib import Path

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


def quicktype(base_bath: Path, schema: str, out_file: Path) -> None:
    """Generate models from JSON schema."""
    # Write json schema to file.
    json_file = base_bath.joinpath(f"{uuid.uuid4()}.json")
    json_file.touch()
    json_file.write_text(schema)
    # Use quicktype
    subprocess.call(["quicktype", "-s", "schema", json_file, "-o", out_file])
    os.remove(json_file)
