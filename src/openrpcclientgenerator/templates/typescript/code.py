# Models
data_class = """
export class {name} {{
{fields}

  constructor({args}) {{
{initiations}
  }}

  toJSON() {{
    return {{
{to_json}
    }}
  }}

  static fromJSON(data: any): {name} {{
    let instance = new {name};
{from_json}
    return instance;
  }}
}}
"""

# Methods
client = """
import * as m from "./models.js";
import {{RPCHTTPClient}} from "jsonrpc2-tsclient";

export class {name}HTTPClient extends RPCHTTPClient {{
  constructor(url: string, headers?: object) {{
    super(url, headers);
  }}
{methods}
}}

function _toJSON(objects: any[]) {{
  return objects.map(it => it?.hasOwnProperty('toJSON') ? it.toJSON() : it);
}}
"""
method = """
  async {name}({args}): Promise<{return_type}> {{
    let params = _toJSON([{params}]);
    let result = await this.call('{method}', params);
    {result_casting}
    return result;
  }}
"""

from_json = """
if ({return_type}.hasOwnProperty('fromJSON')) {{
      result = {return_type}.fromJSON(result);
    }}
"""

array_from_json = """
if ({return_type}.hasOwnProperty('fromJSON')) {{
      result = result.map(it => {return_type}.fromJSON(it));
    }}
"""
