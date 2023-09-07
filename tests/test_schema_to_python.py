"""Test JSON schema to Python type."""
from openrpc import Schema

from models import (
    CollectionsModel,
    Constantly,
    ConstrainedCollections,
    Defaults,
    Primitives,
    PydanticExtra,
    PydanticNetworkTypes,
    PydanticTypes,
    PythonTypes,
    RecursiveModel,
    VanillaModel,
)
from openrpcclientgenerator import python


def test_primitives() -> None:
    schema = Schema(**Primitives.model_json_schema())
    assert python.py_type(schema.properties["int_field"]) == "int"
    assert python.py_type(schema.properties["float_field"]) == "float"
    assert python.py_type(schema.properties["str_field"]) == "str"
    assert python.py_type(schema.properties["bool_field"]) == "bool"
    assert python.py_type(schema.properties["bytes_field"]) == "bytes"
    assert python.py_type(schema.properties["none_field"]) == "None"


def test_python_types() -> None:
    schema = Schema(**PythonTypes.model_json_schema())
    assert python.py_type(schema.properties["str_enum"]) == "Flavor"
    assert python.py_type(schema.properties["num_enum"]) == "Numbers"
    assert python.py_type(schema.properties["date"]) == "datetime.date"
    assert python.py_type(schema.properties["time"]) == "datetime.time"
    assert python.py_type(schema.properties["datetime_field"]) == "datetime.datetime"
    assert python.py_type(schema.properties["timedelta"]) == "datetime.timedelta"
    assert python.py_type(schema.properties["uuid_field"]) == "UUID"
    assert python.py_type(schema.properties["decimal"]) == "float | str"


def test_defaults() -> None:
    schema = Schema(**Defaults.model_json_schema())
    assert python.py_type(schema.properties["str_field"]) == ""
    assert python.py_type(schema.properties["int_field"]) == ""
    assert python.py_type(schema.properties["float_field"]) == ""
    assert python.py_type(schema.properties["bool_true"]) == ""
    assert python.py_type(schema.properties["bool_false"]) == ""
    assert python.py_type(schema.properties["list_field"]) == ""


def test_constantly() -> None:
    schema = Schema(**Constantly.model_json_schema())


def test_vanilla_model() -> None:
    schema = Schema(**VanillaModel.model_json_schema())


def test_recursive_model() -> None:
    schema = Schema(**RecursiveModel.model_json_schema())


def test_collections_model() -> None:
    schema = Schema(**CollectionsModel.model_json_schema())


def test_constrained_collections() -> None:
    schema = Schema(**ConstrainedCollections.model_json_schema())


def test_pydantic_types() -> None:
    schema = Schema(**PydanticTypes.model_json_schema())


def test_pydantic_network_types() -> None:
    schema = Schema(**PydanticNetworkTypes.model_json_schema())


def test_pydantic_extra() -> None:
    schema = Schema(**PydanticExtra.model_json_schema())
