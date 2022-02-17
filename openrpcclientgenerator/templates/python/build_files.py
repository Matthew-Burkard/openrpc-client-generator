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
    pydantic~=1.9.0
    jsonrpc2-objects~=2.0.0
    jsonrpc2-pyclient~=2.1.1

[options.packages.find]
where = {pkg_dir}
"""

py_project = """
[build-system]
requires = ["wheel", "setuptools"]
build-backend = "setuptools.build_meta"
"""
