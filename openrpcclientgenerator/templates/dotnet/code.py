"""C# code templates."""

# Models
class_file = """
using System.Collections.Generic;
using System.Runtime.Serialization;
using Newtonsoft.Json;

namespace {namespace}
{{
{classes}
}}
""".strip()

data_class = """
    {doc}
    [DataContract]
    public class {name}
    {{
        {fields}
    }}
""".rstrip()
field = '[JsonProperty("{prop_name}"{req})] public {type} {name} {{ get; set; }}'

# Methods
client_file = """
using System.Collections.Generic;
using System.Threading.Tasks;
using JsonRpcClient.Clients;
using Newtonsoft.Json;

namespace {namespace}
{{
    public class {title}{transport}Client : Rpc{transport}Client
    {{
        public {title}{transport}Client(string baseUri) : base(baseUri)
        {{
        }}

{methods}
    }}
}}
"""

method = """
        /**
        {doc}
         */
        public async Task<{return_type}> {name}({args})
        {{
            var v = await Call("{method}", {params});
            if (v is {return_type} t)
            {{
                return t;
            }}

            return JsonConvert.DeserializeObject<{return_type}>(v.ToString()!);
        }}
""".removeprefix(
    "\n"
)
