"""Get TypeScript project files."""
from typing import Iterable

index_ts = """
import {{{name}{transport}Client}} from "./client.js";
import {{{models}}} from "./models.js";

export {{{name}{transport}Client, {models}}};
""".lstrip()

tsconfig = """
{
  "compilerOptions": {
    "outDir": "dist",
    "target": "es2020",
    "module": "es2020",
    "rootDir": "src",
    "moduleResolution": "Node",
    "declaration": true,
    "removeComments": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "lib"]
}
""".lstrip()

package_json = """
{{
  "name": "{name}",
  "version": "{version}",
  "description": "{description}",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["/dist"],
  "scripts": {{
    "build": "tsc"
  }},
  "dependencies": {{
    "jsonrpc2-tsclient": "^1.3.9"
  }},
  "author": "{author}",
  "license": "{license}"
}}
""".lstrip()


def get_index_ts(rpc_title: str, schema_names: Iterable[str], transport: str) -> str:
    """Get `index.ts` file content."""
    return index_ts.format(
        name=rpc_title, transport=transport, models=", ".join(schema_names)
    )


def get_package_json(
    name: str, rpc_version: str, rpc_description: str, author: str, license_: str
) -> str:
    """Get `index.ts` file content."""
    return package_json.format(
        name=name,
        version=rpc_version,
        description=rpc_description,
        author=author,
        license=license_,
    )


def get_ts_config() -> str:
    """Get Typescript config file content."""
    return tsconfig
