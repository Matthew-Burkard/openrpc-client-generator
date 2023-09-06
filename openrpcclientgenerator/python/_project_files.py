"""Get Python project files."""

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
pydantic = "^2.0.3"
jsonrpc2-objects = "^3.0.0"
jsonrpc2-pyclient = "^2.1.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip()


def get_pyproject(pkg_name: str, version: str, author: str, email: str) -> str:
    """Get pyproject file content."""
    return py_project.format(
        name=pkg_name,
        version=version,
        author=author,
        author_email=email,
        pkg_dir=f"src/{pkg_name}",
    )
