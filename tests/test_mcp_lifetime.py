import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
from agentsumo.client import stdio_transport


@pytest.mark.parametrize('fail_initialization', [False, True])
def test_transport_closes_resources_in_the_opening_task(monkeypatch, fail_initialization):
    events = []

    @asynccontextmanager
    async def connection(_):
        owner = asyncio.current_task()
        events.append('open')
        try:
            yield (None, None)
        finally:
            assert asyncio.current_task() is owner
            events.append('close')

    class Session:
        def __init__(self, *_): pass
        async def __aenter__(self):
            self.owner = asyncio.current_task()
            return self
        async def __aexit__(self, *_):
            assert asyncio.current_task() is self.owner
            events.append('session-close')
        async def initialize(self):
            if fail_initialization:
                raise RuntimeError('Handshake failed')

    monkeypatch.setattr(stdio_transport, 'stdio_client', connection)
    monkeypatch.setattr(stdio_transport, 'ClientSession', Session)

    async def run():
        transport = stdio_transport.OwnedStdioSession()
        if fail_initialization:
            with pytest.raises(RuntimeError, match='Handshake failed'):
                await transport.start(SimpleNamespace(), 1)
        else:
            await asyncio.create_task(transport.start(SimpleNamespace(), 1))
            await asyncio.create_task(transport.close())
        assert transport.session is None

    asyncio.run(run())
    assert events == ['open', 'session-close', 'close']
