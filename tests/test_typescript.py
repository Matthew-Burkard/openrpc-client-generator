"""Test TypeScript generation."""
import common
from openrpcclientgenerator import typescript


def test_get_method() -> None:
    typescript._get_client._get_method()


# noinspection PyUnresolvedReferences
def test_primitive_types() -> None:
    assert typescript._common.get_ts_type(common.number) == "number"
    assert typescript._common.get_ts_type(common.integer) == "integer"
    assert typescript._common.get_ts_type(common.string) == "string"
    assert typescript._common.get_ts_type(common.boolean) == "boolean"
    assert typescript._common.get_ts_type(common.null) == "null"


def test_schemas() -> None:
    # noinspection PyUnresolvedReferences
    typescript._common.get_ts_type()


def test_get_models() -> None:
    typescript.get_models()


def test_get_index_ts() -> None:
    typescript.get_index_ts()


def test_get_package_json() -> None:
    typescript.get_package_json()


def test_get_ts_config() -> None:
    typescript.get_ts_config()
