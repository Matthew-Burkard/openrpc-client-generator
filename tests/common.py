"""Properties used in all client unit tests."""
from openrpc import SchemaObject


number = SchemaObject(type="number")
integer = SchemaObject(type="integer")
string = SchemaObject(type="string")
boolean = SchemaObject(type="boolean")
null = SchemaObject(type="null")

default_number = SchemaObject(type="number", default=3.14)
default_integer = SchemaObject(type="integer", default=70)
default_string = SchemaObject(type="string", default="string")
default_boolean = SchemaObject(type="boolean", default=True)
default_null = SchemaObject(type="null", default=None)

plain_array = SchemaObject(type="array")
property_array = SchemaObject(type="array", items=number)
array_array = SchemaObject(type="array", items=property_array)

plain_object = SchemaObject(type="object")
properties_object = SchemaObject(type="object", properties={"a": number})
additional_properties_object = SchemaObject(type="apo", additionalProperties=number)
nested_properties = SchemaObject(type="np", properties={"a": properties_object})
