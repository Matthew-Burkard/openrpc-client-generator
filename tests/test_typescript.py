"""Test TypeScript generation."""
import inspect

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
    model_match = inspect.cleandoc(
        """
        export class ParentModel {
          dateField: string;
          recursiveField: ParentModel;
          childField?: TestModel;

          constructor(dateField?: string, childField?: TestModel, recursiveField?: ParentModel) {
            this.dateField = dateField;
            this.childField = childField;
            this.recursiveField = recursiveField;
          }

          toJSON() {
            return {
              date_field: toJSON(this.dateField),
              child_field: toJSON(this.childField),
              recursive_field: toJSON(this.recursiveField),
            }
          }

          static fromJSON(data: any): ParentModel {
            let instance = new ParentModel();
            instance.dateField = fromJSON(data.date_field);
            instance.childField = fromJSON(data.child_field);
            instance.recursiveField = fromJSON(data.recursive_field);
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
    )
    assert model_str == f"\n{model_match}\n"
