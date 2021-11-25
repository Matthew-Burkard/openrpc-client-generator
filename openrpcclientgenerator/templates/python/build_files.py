"""Python project file templates."""

setup = """
[metadata]
name = {name}
version = {version}
author = {author}
author_email = {author_email}
description = Python client for {name} server.
classifiers = Programming Language :: Python :: 3

[options]
package_dir =
    = {pkg_dir}
packages = find:
python_requires = >=3.9
install_requires =
    pydantic~=1.8.2
    jsonrpc2-objects~=1.3.0
    jsonrpc2-pyclient~=1.0.0

[options.packages.find]
where = {pkg_dir}
"""

py_project = """
[build-system]
requires = ["wheel", "setuptools"]
build-backend = "setuptools.build_meta"
"""
