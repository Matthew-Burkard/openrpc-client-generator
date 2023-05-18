"""Provides the ClientFactory class."""
import os
import shutil
import subprocess
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

import caseswitcher as cs
from openrpc import ContactObject, OpenRPCObject, SchemaObject

from openrpcclientgenerator import _util
from openrpcclientgenerator.generators.dotnet import CSharpCodeGenerator
from openrpcclientgenerator.generators.kotlin import KotlinCodeGenerator
from openrpcclientgenerator.generators.python import PythonCodeGenerator
from openrpcclientgenerator.generators.transports import Transport
from openrpcclientgenerator.generators.typescript import TypeScriptGenerator
from openrpcclientgenerator.templates.dotnet import dotnet_files
from openrpcclientgenerator.templates.python import build_files as py_build_files
from openrpcclientgenerator.templates.typescript import (
    build_files as ts_build_files,
    prettier,
)
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

    def __init__(self, rpc: OpenRPCObject, out_dir: str | os.PathLike) -> None:
        """Init a ClientFactory instance.

        :param out_dir: Directory to place generated clients. A
            subdirectory will be made for each language generated.
        :param rpc: OpenRPC document object.
        """
        self.rpc = rpc
        self.rpc.info.contact = self.rpc.info.contact or ContactObject()
        self.rpc.info.contact.name = self.rpc.info.contact.name or "Not Provided"
        self.rpc.info.contact.email = self.rpc.info.contact.email or "Not Provided"
        self._schemas = _util.get_schemas(rpc.components.schemas)
        self._out_dir = Path(out_dir)

    def generate_client(
        self,
        language: Language,
        transport: Transport,
        build: bool = True,
        remove_existing: bool = False,
    ) -> str:
        """Generate an RPC client for the given language.

        :param language: Language to generate code of.
        :param transport: Client transport protocol.
        :param build: Build/pack the client into a tarball.
        :param remove_existing: Replace existing clients of the same
            version.
        :return: Path to client tarball if it exists, else root dir.
        """
        if not remove_existing and self._client_exists(language):
            return self._get_tarball_path(language)
        return {  # type: ignore
            Language.DOTNET: self._generate_dotnet_client,
            Language.KOTLIN: self._generate_kotlin_client,
            Language.PYTHON: self._generate_python_client,
            Language.TYPE_SCRIPT: self._generate_typescript_client,
        }[language].__call__(build, transport)

    def _generate_dotnet_client(self, build: bool, transport: Transport) -> str:
        generator = CSharpCodeGenerator(self.rpc, self._schemas)
        sln_name = f"{cs.to_dot(self.rpc.info.title)}.client"
        client_path = self._out_dir / "dotnet" / sln_name
        shutil.rmtree(client_path, ignore_errors=True)
        package_path = client_path / sln_name
        os.makedirs(package_path, exist_ok=True)
        # Models
        if self._schemas:
            model_file = package_path / "Models.cs"
            models = SchemaObject(properties=self._schemas)
            schema = models.json(exclude_unset=True, by_alias=True)
            schema = schema.replace("components/schemas", "properties")
            _util.quicktype(package_path, schema, model_file)
        # Methods
        client_str = generator.get_client(transport)
        client_file = package_path / "Client.cs"
        client_file.touch()
        client_file.write_text(client_str)
        # Build files
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
            subprocess.run(["dotnet", "pack", solution_file])
            bin_dir = f"{client_path}/{sln_name}/bin"
            return f"{bin_dir}/Debug/{sln_name}.{self.rpc.info.version}.nupkg"
        return client_path.as_posix()

    def _generate_kotlin_client(self, build: bool, transport: Transport) -> str:
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
        client_str = generator.get_client(transport)
        client_file = package_path / "Client.kt"
        client_file.touch()
        client_file.write_text(client_str)
        if build:
            pass  # TODO
        return client_path.as_posix()

    def _generate_python_client(self, build: bool, transport: Transport) -> str:
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
            subprocess.run(["black", models_file])
        # Methods
        client_str = generator.get_client(transport)
        client_file = package_path / "client.py"
        client_file.touch()
        client_file.write_text(client_str)
        subprocess.run(["black", client_file])
        # Build Files
        py_proj_toml = client_path / "pyproject.toml"
        py_proj_toml.write_text(
            py_build_files.py_project.format(
                name=pkg_name,
                version=self.rpc.info.version,
                author=self.rpc.info.contact.name,
                author_email=self.rpc.info.contact.email,
                pkg_dir=f"src/{pkg_name}",
            )
        )
        # Build client.
        if build:
            old_pwd = os.getcwd()
            os.chdir(client_path)
            subprocess.run(["poetry", "build"])
            os.chdir(old_pwd)
            return f"{client_path}/dist/{pkg_name}-{self.rpc.info.version}.tar.gz"
        return client_path.as_posix()

    def _generate_typescript_client(self, build: bool, transport: Transport) -> str:
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
        client_str = generator.get_client(transport)
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
        # Prettier
        prettier_rc = client_path / ".prettierrc"
        prettier_rc.touch()
        prettier_rc.write_text(prettier.prettier_rc)
        prettier_ignore = client_path / ".prettierignore"
        prettier_ignore.touch()
        prettier_ignore.write_text(prettier.prettier_ignore)
        subprocess.run(["npx", "prettier", "--write", client_path])
        # Build Client
        if build:
            subprocess.run(["npm", "i", "--prefix", client_path])
            subprocess.run(["npm", "run", "build", "--prefix", client_path])
            subprocess.run(["npm", "pack", client_path])
            tarball = f"{pkg_name}-{self.rpc.info.version}.tgz"
            shutil.move(f"{os.getcwd()}/{tarball}", f"{client_path}/{tarball}")
            return f"{client_path}/{tarball}"
        return client_path.as_posix()

    def _client_exists(self, language: Language) -> bool:
        match language:
            case Language.DOTNET:
                return Path(self._get_tarball_path(language)).exists()
            case Language.KOTLIN:
                return False
            case Language.PYTHON:
                return Path(self._get_tarball_path(language)).exists()
            case Language.TYPE_SCRIPT:
                return Path(self._get_tarball_path(language)).exists()

    def _get_tarball_path(self, language: Language) -> str:
        version = self.rpc.info.version
        match language:
            case Language.DOTNET:
                sln_name = f"{cs.to_pascal(self.rpc.info.title)}Client"
                debug_path = self._out_dir / "dotnet" / sln_name / "bin" / "Debug"
                nupkg = debug_path / "net472" / f"{sln_name}.{version}.nupkg"
                return Path(nupkg).as_posix()
            case Language.KOTLIN:
                return Path().as_posix()
            case Language.PYTHON:
                pkg_name = f"{cs.to_snake(self.rpc.info.title)}_client"
                client_dir = self._out_dir / "python" / pkg_name
                tarball = client_dir / "dist" / f"{pkg_name}-{version}.tar.gz"
                return Path(tarball).as_posix()
            case Language.TYPE_SCRIPT:
                pkg_name = f"{cs.to_snake(self.rpc.info.title)}_client"
                client_dir = self._out_dir / "typescript" / pkg_name
                tarball = client_dir / f"{pkg_name}-{version}.tgz"
                return Path(tarball).as_posix()
