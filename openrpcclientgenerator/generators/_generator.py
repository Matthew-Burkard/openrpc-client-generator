"""Provides an abstract class for code generators to extend."""
import abc

from openrpc.objects import OpenRPCObject, SchemaObject

from openrpcclientgenerator.generators.transports import Transport


class CodeGenerator(abc.ABC):
    """Defines methods for RPC client generators."""

    def __init__(
        self, openrpc: OpenRPCObject, schemas: dict[str, SchemaObject]
    ) -> None:
        self.openrpc = openrpc
        self.schemas = schemas

    @abc.abstractmethod
    def get_client(self, transport: Transport = Transport.HTTP) -> str:
        """Get an RPC client."""
        ...

    @abc.abstractmethod
    def get_models(self) -> str:
        """Get models."""
        ...
