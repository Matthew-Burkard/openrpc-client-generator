"""Test OpenRPC Server."""
from __future__ import annotations

import asyncio

from openrpc import RPCServer
from pydantic import BaseModel
from sanic import Request, Sanic, Websocket

app = Sanic("TestServer")
rpc = RPCServer(title="TestServer", version="1.0.0")
connected_clients = []


class Person(BaseModel):
    """A person."""

    name: str
    age: int
    parent: Person | None = None


@rpc.method()
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@rpc.method()
async def divide(a: int, b: int) -> float:
    """Divide two integers."""
    return a / b


@rpc.method()
async def create_person(name: str, age: int, parent: Person | None = None) -> Person:
    """Create a person."""
    return Person(name=name, age=age, parent=parent)


@app.websocket("/api/v1/")
async def ws_process_rpc(_request: Request, ws: Websocket) -> None:
    """Process RPC requests through websocket."""

    async def _process_rpc(request: str) -> None:
        json_rpc_response = await rpc.process_request_async(request)
        if json_rpc_response is not None:
            await ws.send(json_rpc_response)

    async for msg in ws:
        asyncio.create_task(_process_rpc(msg))


if __name__ == "__main__":
    app.run(port=8080)
