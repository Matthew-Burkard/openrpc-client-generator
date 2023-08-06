"""Client generator unit tests."""
import json
import os
import unittest
from pathlib import Path

from openrpc import OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory, Language
from openrpcclientgenerator.generators.transports import Transport

remove_existing = not bool(os.environ.get("KEEP_EXISTING_CLIENT"))


class RPCTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        pwd = os.getcwd()
        test_openrpc_doc = OpenRPCObject(
            **json.loads(Path(f"{pwd}/integration/test_openrpc.json").read_text())
        )
        self.test_cf = ClientFactory(test_openrpc_doc, f"{pwd}/../dist/generated")
        math_openrpc_doc = OpenRPCObject(
            **json.loads(Path(f"{pwd}/integration/math_openrpc.json").read_text())
        )
        self.math_cf = ClientFactory(math_openrpc_doc, f"{pwd}/../dist/generated")
        super(RPCTest, self).__init__(*args)

    def test_kotlin(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    language=Language.KOTLIN,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_python(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    language=Language.PYTHON,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_typescript(self) -> None:
        self.assertEqual(
            str,
            type(
                self.test_cf.generate_client(
                    language=Language.TYPE_SCRIPT,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_kotlin_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    language=Language.KOTLIN,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_python_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    language=Language.PYTHON,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_typescript_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    language=Language.TYPE_SCRIPT,
                    transport=Transport.HTTP,
                    remove_existing=remove_existing,
                )
            ),
        )
