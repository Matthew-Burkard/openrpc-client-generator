"""Test Dotnet clients."""
import json
import os
import unittest
from pathlib import Path

from openrpc import OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory, Language
from openrpcclientgenerator.generators.transports import Transport

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
                    language=Language.DOTNET,
                    transport=Transport.WS,
                    build=build,
                    remove_existing=remove_existing,
                )
            ),
        )

    def test_dotnet_no_models(self) -> None:
        self.assertEqual(
            str,
            type(
                self.math_cf.generate_client(
                    language=Language.DOTNET,
                    transport=Transport.WS,
                    build=build,
                    remove_existing=remove_existing,
                )
            ),
        )
