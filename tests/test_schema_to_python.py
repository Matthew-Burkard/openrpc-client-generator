"""Test JSON schema to Python type."""
from openrpc import Schema

from test_models import (
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
    assert _pytype(schema, "int_field") == "int"
    assert _pytype(schema, "float_field") == "float"
    assert _pytype(schema, "str_field") == "str"
    assert _pytype(schema, "bool_field") == "bool"
    assert _pytype(schema, "bytes_field") == "bytes"
    assert _pytype(schema, "none_field") == "None"


def test_python_types() -> None:
    schema = Schema(**PythonTypes.model_json_schema())
    assert _pytype(schema, "str_enum") == "Flavor"
    assert _pytype(schema, "num_enum") == "Numbers"
    assert _pytype(schema, "date") == "datetime.date"
    assert _pytype(schema, "time") == "datetime.time"
    assert _pytype(schema, "datetime_field") == "datetime.datetime"
    assert _pytype(schema, "timedelta") == "datetime.timedelta"
    assert _pytype(schema, "uuid_field") == "UUID"
    assert _pytype(schema, "decimal") == "float | str"


def test_defaults() -> None:
    schema = Schema(**Defaults.model_json_schema())
    assert _pytype(schema, "str_field") == "str"
    assert _pytype(schema, "int_field") == "int"
    assert _pytype(schema, "float_field") == "float"
    assert _pytype(schema, "bool_true") == "bool"
    assert _pytype(schema, "bool_false") == "bool"
    assert _pytype(schema, "list_field") == "list[str] | None"


def test_constantly() -> None:
    schema = Schema(**Constantly.model_json_schema())
    assert _pytype(schema, "const_str_field") == 'Literal["Cat."]'
    assert _pytype(schema, "const_num_field") == "Literal[3]"
    assert _pytype(schema, "const_none_field") == "Literal[None]"
    assert _pytype(schema, "const_true_field") == "Literal[True]"
    assert _pytype(schema, "const_false_field") == "Literal[False]"


def test_recursive_model() -> None:
    schema = Schema(**RecursiveModel.model_json_schema())
    assert python.py_type(schema) == "RecursiveModel"
    assert (
        python.py_type(schema.defs["RecursiveModel"].properties["child"])
        == "RecursiveModel | None"
    )


def test_collections_model() -> None:
    schema = Schema(**CollectionsModel.model_json_schema())
    assert _pytype(schema, "list_field") == "list[Any]"
    assert _pytype(schema, "list_str") == "list[str]"
    assert _pytype(schema, "list_list") == "list[list[Any]]"
    assert _pytype(schema, "list_list_int") == "list[list[int]]"
    assert _pytype(schema, "list_model") == "list[VanillaModel]"
    assert (
        _pytype(schema, "list_model_or_model") == "list[VanillaModel | RecursiveModel]"
    )
    assert _pytype(schema, "list_union") == "list[str | int]"
    assert _pytype(schema, "list_dict") == "list[dict[str, Any]]"
    assert _pytype(schema, "list_dict_str") == "list[dict[str, str]]"
    assert _pytype(schema, "list_dict_int_keys") == "list[dict[str, str]]"
    assert _pytype(schema, "tuple_field") == "list[Any]"
    assert _pytype(schema, "tuple_str") == "tuple[str]"
    assert _pytype(schema, "tuple_tuple") == "tuple[list[Any]]"
    assert _pytype(schema, "tuple_tuple_int") == "tuple[tuple[int]]"
    assert _pytype(schema, "tuple_model") == "tuple[VanillaModel]"
    assert _pytype(schema, "tuple_union") == "tuple[str | int]"
    assert _pytype(schema, "tuple_int_str_none") == "tuple[int, str, None]"
    assert _pytype(schema, "set_str") == "set[str]"
    assert _pytype(schema, "set_union") == "set[str | int]"
    assert _pytype(schema, "dict_field") == "dict[str, Any]"
    assert _pytype(schema, "dict_str") == "dict[str, str]"
    assert _pytype(schema, "dict_dict") == "dict[str, dict[str, Any]]"
    assert _pytype(schema, "dict_int_keys") == "dict[str, str]"
    assert _pytype(schema, "dict_model") == "dict[str, VanillaModel]"
    assert (
        _pytype(schema, "dict_model_or_model")
        == "dict[str, VanillaModel | RecursiveModel]"
    )
    assert _pytype(schema, "dict_union") == "dict[str, str | int]"
    assert _pytype(schema, "dict_list") == "dict[str, list[int]]"


def test_constrained_collections() -> None:
    schema = Schema(**ConstrainedCollections.model_json_schema())
    assert _pytype(schema, "list_min") == "list[Any]"
    assert _pytype(schema, "list_max") == "list[str]"
    assert _pytype(schema, "list_min_max") == "list[str]"


def test_pydantic_types() -> None:
    schema = Schema(**PydanticTypes.model_json_schema())
    assert _pytype(schema, "strict_bool") == "bool"
    assert _pytype(schema, "positive_int") == "int"
    assert _pytype(schema, "negative_int") == "int"
    assert _pytype(schema, "non_positive_int") == "int"
    assert _pytype(schema, "non_negative_int") == "int"
    assert _pytype(schema, "strict_int") == "int"
    assert _pytype(schema, "positive_float") == "float"
    assert _pytype(schema, "negative_float") == "float"
    assert _pytype(schema, "non_positive_float") == "float"
    assert _pytype(schema, "non_negative_float") == "float"
    assert _pytype(schema, "strict_float") == "float"
    assert _pytype(schema, "finite_float") == "float"
    assert _pytype(schema, "strict_bytes") == "bytes"
    assert _pytype(schema, "strict_str") == "str"
    assert _pytype(schema, "uuid1") == "UUID1"
    assert _pytype(schema, "uuid3") == "UUID3"
    assert _pytype(schema, "uuid4") == "UUID4"
    assert _pytype(schema, "uuid5") == "UUID5"
    assert _pytype(schema, "base64bytes") == "str"
    assert _pytype(schema, "base64str") == "str"
    assert _pytype(schema, "str_constraints_strip_whitespace") == "str"
    assert _pytype(schema, "str_constraints_to_upper") == "str"
    assert _pytype(schema, "str_constraints_to_lower") == "str"
    assert _pytype(schema, "str_constraints_strict") == "str"
    assert _pytype(schema, "str_constraints_min_length") == "str"
    assert _pytype(schema, "str_constraints_max_length") == "str"
    assert _pytype(schema, "json_field") == "str"
    assert _pytype(schema, "past_date") == "datetime.date"
    assert _pytype(schema, "future_date") == "datetime.date"
    assert _pytype(schema, "aware_datetime") == "datetime.datetime"
    assert _pytype(schema, "naive_datetime") == "datetime.datetime"
    assert _pytype(schema, "past_datetime") == "datetime.datetime"
    assert _pytype(schema, "future_datetime") == "datetime.datetime"


def test_pydantic_network_types() -> None:
    schema = Schema(**PydanticNetworkTypes.model_json_schema())
    assert _pytype(schema, "any_url") == "str"
    assert _pytype(schema, "any_http_url") == "str"
    assert _pytype(schema, "http_url") == "str"
    assert _pytype(schema, "postgres_dsn") == "str"
    assert _pytype(schema, "cockroach_dsn") == "str"
    assert _pytype(schema, "amqp_dsn") == "str"
    assert _pytype(schema, "redis_dsn") == "str"
    assert _pytype(schema, "mongo_dsn") == "str"
    assert _pytype(schema, "kafka_dsn") == "str"
    assert _pytype(schema, "mysql_dsn") == "str"
    assert _pytype(schema, "mariadb_dsn") == "str"
    assert _pytype(schema, "email_str") == "str"
    assert _pytype(schema, "name_email") == "str"
    assert _pytype(schema, "ipv_any_address") == "str"
    assert _pytype(schema, "ipv_any_interface") == "str"
    assert _pytype(schema, "ipv_any_network") == "str"


def test_pydantic_extra() -> None:
    schema = Schema(**PydanticExtra.model_json_schema())
    assert _pytype(schema, "color") == "str"
    assert _pytype(schema, "payment_card_brand") == "PaymentCardBrand"
    assert _pytype(schema, "payment_card_number") == "str"
    assert _pytype(schema, "aba_routing_number") == "str"


def test_remaining() -> None:
    assert python.py_type(None) == "Any"
    assert python.py_type(True) == "Any"
    assert python.py_type(Schema(type=["string", "integer"])) == "str | int"


def _pytype(schema: Schema, prop: str) -> str:
    return python.py_type(schema.properties[prop])
