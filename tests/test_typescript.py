"""Test TypeScript generation."""
import inspect
import re

import common
from openrpcclientgenerator import typescript


def test_get_method() -> None:
    method_str = typescript._get_client._get_method(common.method)
    assert inspect.cleandoc(method_str) == inspect.cleandoc(
        """
          async testMethod(a?: number, b?: string): Promise<object> {
            let params = serializeArrayParams([a, b]);
            let result = await this.call('test_method', params);
            return result as object;
          }
        """
    )


# noinspection PyUnresolvedReferences
def test_primitive_types() -> None:
    assert typescript._common.get_ts_type(common.number) == "number"
    assert typescript._common.get_ts_type(common.integer) == "number"
    assert typescript._common.get_ts_type(common.string) == "string"
    assert typescript._common.get_ts_type(common.boolean) == "boolean"
    assert typescript._common.get_ts_type(common.null) == "null"


# noinspection PyUnresolvedReferences
def test_schemas() -> None:
    assert typescript._common.get_ts_type(common.plain_array) == "any[]"
    assert typescript._common.get_ts_type(common.property_array) == "number[]"
    assert typescript._common.get_ts_type(common.array_array) == "number[][]"

    assert typescript._common.get_ts_type(common.plain_object) == "object"
    assert typescript._common.get_ts_type(common.properties_object) == "object"
    assert (
        typescript._common.get_ts_type(common.additional_properties_object) == "object"
    )
    assert typescript._common.get_ts_type(common.nested_properties) == "object"


def test_get_models() -> None:
    schemas = {"ParentModel": common.parent_model}
    model_str = typescript.get_models(schemas)
    match_groups = re.match(
        r"\nexport class (\w+)\W*(\w*?: \w*?;)\W*(\w*?: \w*?;)", model_str, re.M | re.S
    ).groups()

    class_name = match_groups[0]
    field1 = match_groups[1]
    field2 = match_groups[2]

    assert class_name == "TestModel"
    assert field1 == "numberField: number;"
    assert field2 == "stringField: string;"

    constructor_args = re.match(r".*constructor\((.*?)\)", model_str, re.M | re.S)
    assert constructor_args.groups()[0] == "numberField?: number, stringField?: string"


"""
export class TestModel {
  numberField: number;
  stringField: string;

  constructor(numberField?: number, stringField?: string) {
    this.numberField = numberField;
    this.stringField = stringField;
  }

  toJSON() {
    return {
      number_field: toJSON(this.numberField),
      string_field: toJSON(this.stringField),
    }
  }

  static fromJSON(data: any): TestModel {
    let instance = new TestModel();
    instance.numberField = fromJSON(data.number_field);
    instance.stringField = fromJSON(data.string_field);
    return instance;
  }
}


function fromJSON(obj: any) {
  if (obj !== null && obj !== undefined && obj.hasOwnProperty('fromJSON')) {
    return obj.fromJSON();
  }
  return obj;
}


function toJSON(obj: any) {
  if (obj !== null && obj !== undefined && obj.hasOwnProperty('toJSON')) {
    return obj.toJSON();
  }
  return obj;
}
"""
