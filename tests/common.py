"""Properties used in all client unit tests."""
from openrpc import ContentDescriptorObject, MethodObject, SchemaObject

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
additional_properties_object = SchemaObject(type="object", additionalProperties=number)
nested_properties = SchemaObject(type="object", properties={"a": properties_object})

model = SchemaObject(
    title="TestModel",
    type="object",
    properties={"number_field": number, "string_field": string},
)

method = MethodObject(
    name="test_method",
    params=[
        ContentDescriptorObject(name="a", schema=number),
        ContentDescriptorObject(name="b", schema=string),
    ],
    result=ContentDescriptorObject(name="result", schema=model),
)
