"""TypeScript code templates."""

# Models
models_file = """
{models}

function fromJSON(obj: any) {{
  if (obj !== null && obj !== undefined && obj.hasOwnProperty('fromJSON')) {{
    return obj.fromJSON();
  }}
  return obj;
}}


function toJSON(obj: any) {{
  if (obj !== null && obj !== undefined && obj.hasOwnProperty('toJSON')) {{
    return obj.toJSON();
  }}
  return obj;
}}
""".lstrip()

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
import {{RPC{transport}Client}} from "jsonrpc2-tsclient";


export enum Servers {{
  {servers}
}}


export class {name}{transport}Client extends RPC{transport}Client {{
  constructor(url: string, headers?: object) {{
    super(url, headers);
  }}
{methods}
}}


function serializeArrayParams(array: any[]): any[] {{
  return array.map(it => serializeObject(it));
}}


function serializeObjectParams(obj: any): any {{
  for (const key of Object.keys(obj)) {{
    obj[key] = serializeObject(obj[key]);
  }}
  return obj;
}}


function serializeObject(obj: any): any {{
  if (obj !== null && obj !== undefined && obj.hasOwnProperty('toJSON')) {{
    return obj.toJSON();
  }}
  return obj;
}}
{parameter_interfaces}
""".rstrip()

method = """
  async {name}({args}): Promise<{return_type}> {{
    let params = {params};
    let result = await this.call('{method}', params);
    return {return_value};
  }}
"""
