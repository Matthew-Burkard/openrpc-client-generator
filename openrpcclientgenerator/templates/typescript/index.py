"""TypeScript index file template."""

index_ts = """
import {{{name}HTTPClient}} from "./client.js";
import {{{models}}} from "./models.js";

export {{{name}HTTPClient, {models}}};
""".lstrip()
