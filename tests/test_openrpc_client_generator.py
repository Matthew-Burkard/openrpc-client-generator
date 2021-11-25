"""Client generator unit tests."""
import json
import os
import unittest
from pathlib import Path

from openrpc.objects import OpenRPCObject

from openrpcclientgenerator.client_factory import ClientFactory


# TODO Add more and better unit tests.
class RPCTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        pwd = os.getcwd()
        openrpc_doc = OpenRPCObject(
            **json.loads(Path(f"{pwd}/openrpc.json").read_text())
        )
        self.cf = ClientFactory(f"{pwd}/../dist/generated", openrpc_doc)
        super(RPCTest, self).__init__(*args)

    def test_csharp(self) -> None:
        self.assertEqual(str, type(self.cf.build_c_sharp_client()))

    def test_python(self) -> None:
        self.assertEqual(str, type(self.cf.build_python_client()))

    def test_typescript(self) -> None:
        self.assertEqual(str, type(self.cf.build_typescript_client()))
