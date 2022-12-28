"""Provides an abstract class for code generators to extend."""
import abc

import caseswitcher as cs
from openrpc import OpenRPCObject, SchemaObject

from openrpcclientgenerator.generators.transports import Transport


class CodeGenerator(abc.ABC):
    """Defines methods for RPC client generators."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        """Instantiate CodeGenerator class.

        :param openrpc: OpenRPC doc to generate code from.
        :param schemas: Schemas used.
        """
        self.openrpc = openrpc
        self.schemas = schemas

    @abc.abstractmethod
    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get an RPC client."""

    @abc.abstractmethod
    def get_models(self) -> str:
        """Get models."""

    def _get_servers(self) -> dict[str, str]:
        servers = self.openrpc.servers
        if isinstance(servers, list):
            return {f"{cs.to_upper_snake(s.name)}": f"{s.url}" for s in servers}
        return {f"{cs.to_upper_snake(servers.name)}": f"{servers.url}"}
