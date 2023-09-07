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
    assert python.py_type(schema.properties["str_field"]) == "str"
    assert python.py_type(schema.properties["int_field"]) == "int"
    assert python.py_type(schema.properties["float_field"]) == "float"
    assert python.py_type(schema.properties["bool_true"]) == "bool"
    assert python.py_type(schema.properties["bool_false"]) == "bool"
    assert python.py_type(schema.properties["list_field"]) == "list[str] | None"


def test_constantly() -> None:
    schema = Schema(**Constantly.model_json_schema())
    assert python.py_type(schema.properties["const_str_field"]) == 'Literal["Cat."]'
    assert python.py_type(schema.properties["const_num_field"]) == "Literal[3]"
    assert python.py_type(schema.properties["const_none_field"]) == "Literal[None]"
    assert python.py_type(schema.properties["const_true_field"]) == "Literal[True]"
    assert python.py_type(schema.properties["const_false_field"]) == "Literal[False]"


def test_recursive_model() -> None:
    schema = Schema(**RecursiveModel.model_json_schema())
    assert python.py_type(schema) == "RecursiveModel"
    assert (
        python.py_type(schema.defs["RecursiveModel"].properties["child"])
        == "RecursiveModel | None"
    )


def test_collections_model() -> None:
    schema = Schema(**CollectionsModel.model_json_schema())
    assert python.py_type(schema.properties["list_field"]) == "list[Any]"
    assert python.py_type(schema.properties["list_str"]) == "list[str]"
    assert python.py_type(schema.properties["list_list"]) == "list[list[Any]]"
    assert python.py_type(schema.properties["list_list_int"]) == "list[list[int]]"
    assert python.py_type(schema.properties["list_model"]) == "list[VanillaModel]"
    assert (
        python.py_type(schema.properties["list_model_or_model"])
        == "list[VanillaModel | RecursiveModel]"
    )
    assert python.py_type(schema.properties["list_union"]) == "list[str | int]"
    assert python.py_type(schema.properties["list_dict"]) == "list[dict[str, Any]]"
    assert python.py_type(schema.properties["list_dict_str"]) == "list[dict[str, str]]"
    assert (
        python.py_type(schema.properties["list_dict_int_keys"])
        == "list[dict[str, str]]"
    )
    assert python.py_type(schema.properties["tuple_field"]) == "list[Any]"
    assert python.py_type(schema.properties["tuple_str"]) == "tuple[str]"
    assert python.py_type(schema.properties["tuple_tuple"]) == "tuple[list[Any]]"
    assert python.py_type(schema.properties["tuple_tuple_int"]) == "tuple[tuple[int]]"
    assert python.py_type(schema.properties["tuple_model"]) == "tuple[VanillaModel]"
    assert python.py_type(schema.properties["tuple_union"]) == "tuple[str | int]"
    assert (
        python.py_type(schema.properties["tuple_int_str_none"])
        == "tuple[int, str, None]"
    )
    assert python.py_type(schema.properties["set_str"]) == "set[str]"
    assert python.py_type(schema.properties["set_union"]) == "set[str | int]"
    assert python.py_type(schema.properties["dict_field"]) == "dict[str, Any]"
    assert python.py_type(schema.properties["dict_str"]) == "dict[str, str]"
    assert python.py_type(schema.properties["dict_dict"]) == "dict[str, dict[str, Any]]"
    assert python.py_type(schema.properties["dict_int_keys"]) == "dict[str, str]"
    assert python.py_type(schema.properties["dict_model"]) == "dict[str, VanillaModel]"
    assert (
        python.py_type(schema.properties["dict_model_or_model"])
        == "dict[str, VanillaModel | RecursiveModel]"
    )
    assert python.py_type(schema.properties["dict_union"]) == "dict[str, str | int]"
    assert python.py_type(schema.properties["dict_list"]) == "dict[str, list[int]]"


def test_constrained_collections() -> None:
    schema = Schema(**ConstrainedCollections.model_json_schema())


def test_pydantic_types() -> None:
    schema = Schema(**PydanticTypes.model_json_schema())


def test_pydantic_network_types() -> None:
    schema = Schema(**PydanticNetworkTypes.model_json_schema())


def test_pydantic_extra() -> None:
    schema = Schema(**PydanticExtra.model_json_schema())
