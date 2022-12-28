"""Provides Transport enum."""
from enum import Enum


class Transport(Enum):
    """Enum of supported transport methods for clients."""

    HTTP = "HTTP"
    WS = "WS"
