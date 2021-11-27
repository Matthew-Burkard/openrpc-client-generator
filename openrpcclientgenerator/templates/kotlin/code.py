"""Kotlin code templates."""

# Models
model_file = """
{classes}
""".strip()

model = """
{doc}
data class {name}(
    {fields}
)
"""
field = "val {name}: {type}{default}"

# Methods
client_file = """
class {title}{transport}Client {{
    {methods}
}}
"""

method = """
    /**
     * {doc}
     */
    fun {name}({args}): {return_type} {{
        return this.call({params})
    }}
"""
