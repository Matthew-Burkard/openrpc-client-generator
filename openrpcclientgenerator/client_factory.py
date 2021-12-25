"""Provides the ClientFactory class."""
import os
import shutil
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

import caseswitcher as cs
from build.__main__ import main as build_py
from openrpc.objects import ContactObject, OpenRPCObject

from openrpcclientgenerator import _util
from openrpcclientgenerator.generators.dotnet import CSharpCodeGenerator
from openrpcclientgenerator.generators.kotlin import KotlinCodeGenerator
from openrpcclientgenerator.generators.python import PythonCodeGenerator
from openrpcclientgenerator.generators.typescript import TypeScriptGenerator
from openrpcclientgenerator.templates.dotnet import dotnet_files
from openrpcclientgenerator.templates.python import build_files as py_build_files
from openrpcclientgenerator.templates.typescript import build_files as ts_build_files
from openrpcclientgenerator.templates.typescript.index import index_ts

__all__ = ("ClientFactory", "Language")


class Language(Enum):
    """Languages available to generate clients for."""

    DOTNET = "dotnet"
    KOTLIN = "kotlin"
    PYTHON = "python"
    TYPE_SCRIPT = "typescript"


class ClientFactory:
    """Factory to generate OpenRPC clients for various languages."""

    def __init__(self, out_dir: str, rpc: OpenRPCObject) -> None:
        self.rpc = rpc
        self.rpc.info.contact = self.rpc.info.contact or ContactObject()
        self.rpc.info.contact.name = self.rpc.info.contact.name or "Not Provided"
        self.rpc.info.contact.email = self.rpc.info.contact.email or "Not Provided"
        self._schemas = _util.get_schemas(rpc.components.schemas)
        self._out_dir = Path(out_dir)

    def generate_client(
        self, language: Language, build: bool = False, exists_okay: bool = True
    ) -> str:
        """Generate code for an RPC client.

        :param language: Language to generate code of.
        :param build: If True, build/pack the client.
        :param exists_okay: If True, remove existing code if it exists.
        :return: Path to client package if it was build else root dir.
        """
        return {
            Language.DOTNET: self._generate_dotnet_client,
            Language.KOTLIN: self._generate_kotlin_client,
            Language.PYTHON: self._generate_python_client,
            Language.TYPE_SCRIPT: self._generate_typescript_client,
        }[language].__call__(build, exists_okay)

    def _generate_dotnet_client(self, build: bool, exists_okay: bool) -> str:
        generator = CSharpCodeGenerator(self.rpc, self._schemas)
        sln_name = f"{cs.to_pascal(self.rpc.info.title)}Client"
        client_path = self._out_dir / "dotnet" / sln_name
        package_path = client_path / sln_name
        os.makedirs(package_path, exist_ok=True)
        # Models
        models_str = generator.get_models()
        models_file = package_path / "Models.cs"
        models_file.touch()
        models_file.write_text(models_str)
        # Methods
        client_str = generator.get_client()
        client_file = package_path / "Client.cs"
        client_file.touch()
        client_file.write_text(client_str)
        # Build files.
        solution_file = client_path / f"{sln_name}.sln"
        solution_file.touch()
        solution_file.write_text(
            dotnet_files.solution.format(
                id=str(uuid.uuid4()), name=sln_name, uuid=str(uuid.uuid4())
            )
        )
        csproj_file = package_path / f"{sln_name}.csproj"
        csproj_file.touch()
        csproj_file.write_text(
            dotnet_files.csproj.format(
                name=sln_name,
                version=self.rpc.info.version,
                authors=self.rpc.info.contact.name,
                copyright_holder=self.rpc.info.contact.name,
                description=self.rpc.info.description,
                year=datetime.now().year,
            )
        )
        # Pack client.
        if build:
            os.system(f"dotnet pack {solution_file}")
            bin_dir = f"{client_path}/{sln_name}/bin"
            return f"{bin_dir}/Debug/{sln_name}.{self.rpc.info.version}.nupkg"
        return client_path.as_posix()

    def _generate_kotlin_client(self, build: bool, exists_okay: bool) -> str:
        generator = KotlinCodeGenerator(self.rpc, self._schemas)
        pkg_name = f"{cs.to_pascal(self.rpc.info.title)}Client"
        client_path = self._out_dir / "kotlin" / pkg_name
        package_path = client_path / "src" / pkg_name
        os.makedirs(package_path, exist_ok=True)
        # Models
        models_str = generator.get_models()
        models_file = package_path / "Models.kt"
        models_file.touch()
        models_file.write_text(models_str)
        # Methods
        client_str = generator.get_client()
        client_file = package_path / "Client.kt"
        client_file.touch()
        client_file.write_text(client_str)
        if build:
            pass  # TODO
        return client_path.as_posix()

    def _generate_python_client(self, build: bool, exists_okay: bool) -> str:
        generator = PythonCodeGenerator(self.rpc, self._schemas)
        pkg_name = f"{cs.to_snake(self.rpc.info.title)}_client"
        client_path = self._out_dir / "python" / pkg_name
        package_path = client_path / "src" / pkg_name
        shutil.rmtree(client_path, ignore_errors=True)
        os.makedirs(package_path, exist_ok=True)
        (package_path / "__init__.py").touch()
        # Models
        if self._schemas:
            models_str = generator.get_models()
            models_file = package_path / "models.py"
            models_file.touch()
            models_file.write_text(models_str)
            os.system(f"black {models_file.as_posix()}")
        # Methods
        client_str = generator.get_client()
        client_file = package_path / "client.py"
        client_file.touch()
        client_file.write_text(client_str)
        os.system(f"black {client_file.as_posix()}")
        # Build Files
        setup = client_path / "setup.cfg"
        setup.touch()
        setup.write_text(
            py_build_files.setup.format(
                name=pkg_name,
                version=self.rpc.info.version,
                author=self.rpc.info.contact.name,
                author_email=self.rpc.info.contact.email,
                pkg_dir="src",
            )
        )
        py_proj_toml = client_path / "pyproject.toml"
        py_proj_toml.write_text(py_build_files.py_project)
        # Build client.
        if build:
            build_py([client_path.as_posix()])
            return f"{client_path}/dist/{pkg_name}-{self.rpc.info.version}.tar.gz"
        return client_path.as_posix()

    def _generate_typescript_client(self, build: bool, exists_okay: bool) -> str:
        generator = TypeScriptGenerator(self.rpc, self._schemas)
        pkg_name = f"{cs.to_snake(self.rpc.info.title)}_client"
        client_path = self._out_dir / "typescript" / pkg_name
        shutil.rmtree(client_path, ignore_errors=True)
        src_path = client_path / "src"
        os.makedirs(src_path, exist_ok=True)
        # Models
        if self._schemas:
            models_str = generator.get_models()
            models_file = src_path / "models.ts"
            models_file.touch()
            models_file.write_text(models_str)
        # Methods
        client_str = generator.get_client()
        client_file = src_path / "client.ts"
        client_file.touch()
        client_file.write_text(client_str)
        # Index TS
        index = src_path / "index.ts"
        index.touch()
        index.write_text(
            index_ts.format(
                name=cs.to_pascal(self.rpc.info.title),
                models=", ".join(self._schemas.keys()),
            )
        )
        # Build Files
        tsconfig = client_path / "tsconfig.json"
        tsconfig.touch()
        tsconfig.write_text(ts_build_files.tsconfig)
        package_json = client_path / "package.json"
        package_json.touch()
        package_json.write_text(
            ts_build_files.package_json.format(
                name=pkg_name,
                version=self.rpc.info.version,
                description=f"{self.rpc.info.title} RPC Client.",
                author=self.rpc.info.contact.name,
                license="custom",
            )
        )
        # Build Client
        if build:
            os.system(f"npm i --prefix {client_path}")
            os.system(f"npm run build --prefix {client_path}")
            os.system(f"npm pack {client_path}")
            tarball = f"{pkg_name}-{self.rpc.info.version}.tgz"
            shutil.move(f"{os.getcwd()}/{tarball}", f"{client_path}/{tarball}")
            return f"{client_path}/{tarball}"
        return client_path.as_posix()
