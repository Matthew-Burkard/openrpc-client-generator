import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from openrpc.objects import OpenRPCObject

from openrpcclientgenerator import util
from openrpcclientgenerator.generators.csharp import CSharpGenerator
from openrpcclientgenerator.generators.python import PythonGenerator
from openrpcclientgenerator.generators.typescript import TypeScriptGenerator
from openrpcclientgenerator.templates.csharp import dotnet_files
from openrpcclientgenerator.templates.python import build_files as py_build_files
from openrpcclientgenerator.templates.typescript import build_files as ts_build_files
from openrpcclientgenerator.templates.typescript.index import index_ts

__all__ = ("ClientFactory",)

CLIENT_AUTHOR = os.environ.get("CLIENT_AUTHOR")
CLIENT_AUTHOR_EMAIL = os.environ.get("CLIENT_AUTHOR_EMAIL")
CLIENT_VERSION = os.environ.get("CLIENT_VERSION") or "1.0.0"
CLIENT_COPYRIGHT_HOLDER = os.environ.get("CLIENT_COPYRIGHT_HOLDER")


class ClientFactory:
    def __init__(self, out_dir: str, rpc: OpenRPCObject) -> None:
        self.rpc = rpc
        self._out_dir = Path(out_dir)

    def build_c_sharp_client(self) -> str:
        generator = CSharpGenerator(
            self.rpc.info.title, self.rpc.methods, self.rpc.components.schemas
        )
        sln_name = f"{util.to_pascal_case(self.rpc.info.title)}Client"
        client_path = self._out_dir / "csharp"
        package_path = client_path / sln_name / sln_name
        os.makedirs(package_path, exist_ok=True)
        # Models
        models_str = generator.get_models()
        models_file = package_path / "Models.cs"
        models_file.touch()
        models_file.write_text(models_str)
        # Methods
        methods_str = generator.get_methods()
        methods_file = package_path / "Client.cs"
        methods_file.touch()
        methods_file.write_text(methods_str)
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
                authors=CLIENT_AUTHOR,
                copyright_holder=CLIENT_COPYRIGHT_HOLDER,
                description=self.rpc.info.description,
                year=datetime.now().year,
            )
        )
        # Pack client.
        os.system(f"dotnet pack {solution_file}")
        return client_path.as_posix()

    def build_python_client(self) -> str:
        generator = PythonGenerator(
            self.rpc.info.title, self.rpc.methods, self.rpc.components.schemas
        )
        pkg_name = f"{util.to_snake_case(self.rpc.info.title)}client".replace("_", "")
        client_path = self._out_dir / "python" / pkg_name
        package_path = client_path / "src" / pkg_name
        os.makedirs(package_path, exist_ok=True)
        (package_path / "__init__.py").touch()
        # Models
        models_str = generator.get_models()
        models_file = package_path / "models.py"
        models_file.touch()
        models_file.write_text(models_str)
        # Methods
        methods_str = generator.get_methods()
        methods_file = package_path / "client.py"
        methods_file.touch()
        methods_file.write_text(methods_str)
        # Build Files
        setup = client_path / "setup.cfg"
        setup.touch()
        setup.write_text(
            py_build_files.setup.format(
                name=pkg_name,
                version=CLIENT_VERSION,
                author=CLIENT_AUTHOR,
                author_email=CLIENT_AUTHOR_EMAIL,
                pkg_dir="src",
            )
        )
        py_proj_toml = client_path / "pyproject.toml"
        py_proj_toml.write_text(py_build_files.py_project)
        # Build client.
        os.system(f"python -m build {client_path}")
        return client_path.as_posix()

    def build_typescript_client(self) -> str:
        generator = TypeScriptGenerator(
            self.rpc.info.title, self.rpc.methods, self.rpc.components.schemas
        )
        pkg_name = f"{util.to_snake_case(self.rpc.info.title)}_client"
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
        methods_str = generator.get_methods()
        methods_file = src_path / "client.ts"
        methods_file.touch()
        methods_file.write_text(methods_str)
        # Index TS
        index = src_path / "index.ts"
        index.touch()
        index.write_text(index_ts.format(name=util.to_pascal_case(self.rpc.info.title)))
        # Build Files
        tsconfig = client_path / "tsconfig.json"
        tsconfig.touch()
        tsconfig.write_text(ts_build_files.tsconfig)
        package_json = client_path / "package.json"
        package_json.touch()
        package_json.write_text(
            ts_build_files.package_json.format(
                name=pkg_name,
                version=CLIENT_VERSION,
                description=f"{self.rpc.info.title} RPC Client.",
                author=CLIENT_AUTHOR,
                license="custom",
            )
        )
        # Build Client
        os.system(f"npm i --prefix {client_path}")
        os.system(f"npm run build --prefix {client_path}")
        os.system(f"npm pack {client_path}")
        tarball = f"{pkg_name}-{CLIENT_VERSION}.tgz"
        shutil.move(f"{os.getcwd()}/{tarball}", f"{client_path}/{tarball}")
        return pkg_name
