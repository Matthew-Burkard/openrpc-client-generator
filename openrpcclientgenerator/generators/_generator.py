"""Provides an abstract class for code generators to extend."""
import abc


class Generator(abc.ABC):
    """Defines methods for RPC client generators."""

    @abc.abstractmethod
    def get_client(self, transport="HTTP") -> str:
        """Get an RPC client."""
        ...

    @abc.abstractmethod
    def get_models(self) -> str:
        """Get models."""
        ...
