"""TypeScript project file templates."""

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
