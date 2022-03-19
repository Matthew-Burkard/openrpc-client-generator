"""Python project file templates."""

py_project = """
[tool.poetry]
name = "{name}"
version = "{version}"
description = "Python client for {name} server."
authors = ["{author} <{author_email}>"]
classifiers = ["Programming Language :: Python :: 3"]
packages = [
    {{ include = "{pkg_dir}/**/*.py" }},
]

[tool.poetry.dependencies]
python = "^3.9"
pydantic = "^1.9.0"
jsonrpc2-objects = "^2.0.0"
jsonrpc2-pyclient = "^2.1.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip()
