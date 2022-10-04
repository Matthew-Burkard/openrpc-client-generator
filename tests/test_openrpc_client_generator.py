"""Client generator unit tests."""
import json
import os
import unittest
from pathlib import Path

from openrpc.objects import OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory, Language


build = not bool(os.environ.get("SKIP_BUILD"))
remove_existing = not bool(os.environ.get("KEEP_EXISTING_CLIENT"))


# TODO Add more and better unit tests.
class RPCTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        pwd = os.getcwd()
        test_openrpc_doc = OpenRPCObject(
            **json.loads(Path(f"{pwd}/test_openrpc.json").read_text())
        )
        self.test_cf = ClientFactory(test_openrpc_doc, f"{pwd}/../dist/generated")
        math_openrpc_doc = OpenRPCObject(
            **json.loads(Path(f"{pwd}/math_openrpc.json").read_text())
        )
        self.math_cf = ClientFactory(math_openrpc_doc, f"{pwd}/../dist/generated")
        super(RPCTest, self).__init__(*args)

    def test_dotnet(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    Language.DOTNET, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_kotlin(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    Language.KOTLIN, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_python(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    Language.PYTHON, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_typescript(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    Language.TYPE_SCRIPT, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_dotnet_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    Language.DOTNET, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_kotlin_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    Language.KOTLIN, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_python_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    Language.PYTHON, build=build, remove_existing=remove_existing
                )
            ),
        )

    def test_typescript_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    Language.TYPE_SCRIPT, build=build, remove_existing=remove_existing
                )
            ),
        )
