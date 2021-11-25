"""Provides the ClientFactory class."""
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import caseswitcher as cs
from build.__main__ import main as build
from openrpc.objects import ContactObject, OpenRPCObject

from openrpcclientgenerator import util
from openrpcclientgenerator.generators.csharp import CSharpCodeGenerator
from openrpcclientgenerator.generators.python import PythonCodeGenerator
from openrpcclientgenerator.generators.typescript import TypeScriptGenerator
from openrpcclientgenerator.templates.csharp import dotnet_files
from openrpcclientgenerator.templates.python import build_files as py_build_files
from openrpcclientgenerator.templates.typescript import build_files as ts_build_files
from openrpcclientgenerator.templates.typescript.index import index_ts

__all__ = ("ClientFactory",)


# TODO Server constants.
class ClientFactory:
    """Factory to generate OpenRPC clients for various languages."""

    def __init__(self, out_dir: str, rpc: OpenRPCObject) -> None:
        self.rpc = rpc
        self.rpc.info.contact = self.rpc.info.contact or ContactObject()
        self.rpc.info.contact.name = self.rpc.info.contact.name or "Not Provided"
        self.rpc.info.contact.email = self.rpc.info.contact.email or "Not Provided"
        self._schemas = util.get_schemas(rpc.components.schemas)
        self._out_dir = Path(out_dir)

    def build_c_sharp_client(self, build_client: bool = False) -> str:
        """Generate C# code for an RPC client.

        :param build_client: If True, build the .NET package.
        :return: Path to the .NET client.
        """
        generator = CSharpCodeGenerator(self.rpc, self._schemas)
        sln_name = f"{cs.to_pascal(self.rpc.info.title)}Client"
        client_path = self._out_dir / "csharp"
        package_path = client_path / sln_name / sln_name
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
        solution_file = client_path / sln_name / f"{sln_name}.sln"
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
        if build_client:
            os.system(f"dotnet pack {solution_file}")
        return client_path.as_posix()

    def build_python_client(self, build_client: bool = False) -> str:
        """Generate Python code for an RPC client.

        :param build_client: If True, build the Python package.
        :return: Path to the Python client.
        """
        generator = PythonCodeGenerator(self.rpc, self._schemas)
        title = self.rpc.info.title.lower().replace(" ", "").replace("_", "")
        pkg_name = f"{cs.to_snake(title)}client"
        client_path = self._out_dir / "python" / pkg_name
        package_path = client_path / "src" / pkg_name
        os.makedirs(package_path, exist_ok=True)
        (package_path / "__init__.py").touch()
        # Models
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
        if build_client:
            build([client_path.as_posix()])
        return client_path.as_posix()

    def build_typescript_client(self, build_client: bool = False) -> str:
        """Generate TypeScript code for an RPC client.

        :param build_client: If True, build the TypeScript package.
        :return: Path to the TypeScript client.
        """
        generator = TypeScriptGenerator(self.rpc, self._schemas)
        pkg_name = f"{cs.to_snake(self.rpc.info.title)}_client"
        client_path = self._out_dir / "typescript" / pkg_name
        shutil.rmtree(client_path, ignore_errors=True)
        src_path = client_path / "src"
        os.makedirs(src_path, exist_ok=True)
        # Models
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
        if build_client:
            os.system(f"npm i --prefix {client_path}")
            os.system(f"npm run build --prefix {client_path}")
            os.system(f"npm pack {client_path}")
            tarball = f"{pkg_name}-{self.rpc.info.version}.tgz"
            shutil.move(f"{os.getcwd()}/{tarball}", f"{client_path}/{tarball}")
        return pkg_name