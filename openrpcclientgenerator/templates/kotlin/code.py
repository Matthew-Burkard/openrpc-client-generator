# Models
class_file = """
{classes}
""".strip()

data_class = """
{doc}
data class {name}(
    {fields}
)
"""
field = "{annotation}val {name}: {type}{default}"

# Methods
client_file = """
class {title}{transport}Client {{
    {methods}
}}
"""

method_template = """
    /**
     * {doc}
     */
    fun {name}({args}): {return_type} {{
        return this.call({params})
    }}
"""
