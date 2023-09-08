"""Test JSON schema to TypeScript type."""
from openrpc import Schema

from openrpcclientgenerator import typescript
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


def test_primitives() -> None:
    schema = Schema(**Primitives.model_json_schema())
    assert _tstype(schema, "int_field") == "number"
    assert _tstype(schema, "float_field") == "number"
    assert _tstype(schema, "str_field") == "string"
    assert _tstype(schema, "bool_field") == "boolean"
    assert _tstype(schema, "bytes_field") == "string"
    assert _tstype(schema, "none_field") == "null"


def test_python_types() -> None:
    schema = Schema(**PythonTypes.model_json_schema())
    assert _tstype(schema, "str_enum") == "Flavor"
    assert _tstype(schema, "num_enum") == "Numbers"
    assert _tstype(schema, "date") == "string"
    assert _tstype(schema, "time") == "string"
    assert _tstype(schema, "datetime_field") == "string"
    assert _tstype(schema, "timedelta") == "string"
    assert _tstype(schema, "uuid_field") == "string"
    assert _tstype(schema, "decimal") == "number | string"


def test_defaults() -> None:
    schema = Schema(**Defaults.model_json_schema())
    assert _tstype(schema, "str_field") == "string"
    assert _tstype(schema, "int_field") == "number"
    assert _tstype(schema, "float_field") == "number"
    assert _tstype(schema, "bool_true") == "boolean"
    assert _tstype(schema, "bool_false") == "boolean"
    assert _tstype(schema, "list_field") == "string[] | null"


def test_constantly() -> None:
    schema = Schema(**Constantly.model_json_schema())
    assert _tstype(schema, "const_str_field") == "string"
    assert _tstype(schema, "const_num_field") == "number"
    assert _tstype(schema, "const_none_field") == "null"
    assert _tstype(schema, "const_true_field") == "boolean"
    assert _tstype(schema, "const_false_field") == "boolean"


def test_recursive_model() -> None:
    schema = Schema(**RecursiveModel.model_json_schema())
    assert typescript.ts_type(schema) == "RecursiveModel"
    assert (
        typescript.ts_type(schema.defs["RecursiveModel"].properties["child"])
        == "RecursiveModel | null"
    )


def test_collections_model() -> None:
    schema = Schema(**CollectionsModel.model_json_schema())
    assert _tstype(schema, "list_field") == "any[]"
    assert _tstype(schema, "list_str") == "string[]"
    assert _tstype(schema, "list_list") == "any[][]"
    assert _tstype(schema, "list_list_int") == "number[][]"
    assert _tstype(schema, "list_model") == "VanillaModel[]"
    assert (
            _tstype(schema, "list_model_or_model") == "Array<VanillaModel | RecursiveModel>"
    )
    assert _tstype(schema, "list_union") == "Array<str | int>"
    assert _tstype(schema, "list_dict") == "object[]"
    assert _tstype(schema, "list_dict_str") == "Record<string, string>[]"
    assert _tstype(schema, "list_dict_int_keys") == "Record<string, string>[]"
    assert _tstype(schema, "tuple_field") == "any[]"
    assert _tstype(schema, "tuple_str") == "[string]"
    assert _tstype(schema, "tuple_tuple") == "[any[]]"
    assert _tstype(schema, "tuple_tuple_int") == "[[number]]"
    assert _tstype(schema, "tuple_model") == "[VanillaModel]"
    assert _tstype(schema, "tuple_union") == "[str | int]"
    assert _tstype(schema, "tuple_int_str_none") == "[int, string, null]"
    assert _tstype(schema, "set_str") == "Set<string>"
    assert _tstype(schema, "set_union") == "Set<string | number>"
    assert _tstype(schema, "dict_field") == "object"
    assert _tstype(schema, "dict_str") == "Record<string, string>"
    assert _tstype(schema, "dict_dict") == "Record<string, object>"
    assert _tstype(schema, "dict_int_keys") == "Record<string, string>"
    assert _tstype(schema, "dict_model") == "Record<string, VanillaModel>"
    assert (
            _tstype(schema, "dict_model_or_model")
            == "Record<string, VanillaModel | RecursiveModel>"
    )
    assert _tstype(schema, "dict_union") == "Record<string, string | number>"
    assert _tstype(schema, "dict_list") == "Record<string, number[]>"


def test_constrained_collections() -> None:
    schema = Schema(**ConstrainedCollections.model_json_schema())
    assert _tstype(schema, "list_min") == "any[]"
    assert _tstype(schema, "list_max") == "string[]"
    assert _tstype(schema, "list_min_max") == "string[]"


def test_pydantic_types() -> None:
    schema = Schema(**PydanticTypes.model_json_schema())
    assert _tstype(schema, "strict_bool") == "boolean"
    assert _tstype(schema, "positive_int") == "number"
    assert _tstype(schema, "negative_int") == "number"
    assert _tstype(schema, "non_positive_int") == "number"
    assert _tstype(schema, "non_negative_int") == "number"
    assert _tstype(schema, "strict_int") == "number"
    assert _tstype(schema, "positive_float") == "number"
    assert _tstype(schema, "negative_float") == "number"
    assert _tstype(schema, "non_positive_float") == "number"
    assert _tstype(schema, "non_negative_float") == "number"
    assert _tstype(schema, "strict_float") == "number"
    assert _tstype(schema, "finite_float") == "number"
    assert _tstype(schema, "strict_bytes") == "string"
    assert _tstype(schema, "strict_str") == "string"
    assert _tstype(schema, "uuid1") == "string"
    assert _tstype(schema, "uuid3") == "string"
    assert _tstype(schema, "uuid4") == "string"
    assert _tstype(schema, "uuid5") == "string"
    assert _tstype(schema, "base64bytes") == "string"
    assert _tstype(schema, "base64str") == "string"
    assert _tstype(schema, "str_constraints_strip_whitespace") == "string"
    assert _tstype(schema, "str_constraints_to_upper") == "string"
    assert _tstype(schema, "str_constraints_to_lower") == "string"
    assert _tstype(schema, "str_constraints_strict") == "string"
    assert _tstype(schema, "str_constraints_min_length") == "string"
    assert _tstype(schema, "str_constraints_max_length") == "string"
    assert _tstype(schema, "json_field") == "string"
    assert _tstype(schema, "past_date") == "string"
    assert _tstype(schema, "future_date") == "string"
    assert _tstype(schema, "aware_datetime") == "string"
    assert _tstype(schema, "naive_datetime") == "string"
    assert _tstype(schema, "past_datetime") == "string"
    assert _tstype(schema, "future_datetime") == "string"


def test_pydantic_network_types() -> None:
    schema = Schema(**PydanticNetworkTypes.model_json_schema())
    assert _tstype(schema, "any_url") == "string"
    assert _tstype(schema, "any_http_url") == "string"
    assert _tstype(schema, "http_url") == "string"
    assert _tstype(schema, "postgres_dsn") == "string"
    assert _tstype(schema, "cockroach_dsn") == "string"
    assert _tstype(schema, "amqp_dsn") == "string"
    assert _tstype(schema, "redis_dsn") == "string"
    assert _tstype(schema, "mongo_dsn") == "string"
    assert _tstype(schema, "kafka_dsn") == "string"
    assert _tstype(schema, "mysql_dsn") == "string"
    assert _tstype(schema, "mariadb_dsn") == "string"
    assert _tstype(schema, "email_str") == "string"
    assert _tstype(schema, "name_email") == "string"
    assert _tstype(schema, "ipv_any_address") == "string"
    assert _tstype(schema, "ipv_any_interface") == "string"
    assert _tstype(schema, "ipv_any_network") == "string"


def test_pydantic_extra() -> None:
    schema = Schema(**PydanticExtra.model_json_schema())
    assert _tstype(schema, "color") == "string"
    assert _tstype(schema, "payment_card_brand") == "PaymentCardBrand"
    assert _tstype(schema, "payment_card_number") == "string"
    assert _tstype(schema, "aba_routing_number") == "string"


def test_remaining() -> None:
    assert typescript.ts_type(None) == "any"
    assert typescript.ts_type(True) == "any"
    assert typescript.ts_type(Schema(type=["string", "integer"])) == "string | number"


def _tstype(schema: Schema, prop: str) -> str:
    return typescript.ts_type(schema.properties[prop])
