"""Test TypeScript generation."""
import inspect
import re

import common
from openrpcclientgenerator import python


def test_get_method() -> None:
    async_method_str = python._get_client._get_method(common.method)
    args = "self, a: Optional[float] = None, b: Optional[str] = None"
    assert inspect.cleandoc(async_method_str) == inspect.cleandoc(
        f"""
        async def test_method({args}) -> dict[str, Any]:
            return _deserialize(await self.call('test_method', [a, b]), dict[str, Any])
        """
    )
    method_str = python._get_client._get_method(common.method, is_async=False)
    assert inspect.cleandoc(method_str) == inspect.cleandoc(
        f"""
        def test_method({args}) -> dict[str, Any]:
            return _deserialize(self.call('test_method', [a, b]), dict[str, Any])
        """
    )


# noinspection PyUnresolvedReferences
def test_primitive_types() -> None:
    assert python._common.get_py_type(common.number) == "float"
    assert python._common.get_py_type(common.integer) == "int"
    assert python._common.get_py_type(common.string) == "str"
    assert python._common.get_py_type(common.boolean) == "bool"
    assert python._common.get_py_type(common.null) == "None"


# noinspection PyUnresolvedReferences
def test_schemas() -> None:
    assert python._common.get_py_type(common.plain_array) == "list[Any]"
    assert python._common.get_py_type(common.property_array) == "list[float]"
    assert python._common.get_py_type(common.array_array) == "list[list[float]]"

    assert python._common.get_py_type(common.plain_object) == "dict[str, Any]"
    assert python._common.get_py_type(common.properties_object) == "dict[str, Any]"
    assert (
        python._common.get_py_type(common.additional_properties_object)
        == "dict[str, Any]"
    )
    assert python._common.get_py_type(common.nested_properties) == "dict[str, Any]"


def test_get_models() -> None:
    schemas = {"TestModel": common.model}
    model_str = python.get_models(schemas)
    assert re.match(r".*class TestModel\(BaseModel\):", model_str, re.M | re.S)
    assert re.match(r".*number_field: Optional\[float] = None", model_str, re.M | re.S)
    assert re.match(r".*string_field: Optional\[str] = None", model_str, re.M | re.S)
