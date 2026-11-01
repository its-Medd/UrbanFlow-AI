"""Keep AnyIO MCP resource lifetimes in one owning asyncio task."""
import asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client


class OwnedStdioSession:
    def __init__(self):
        self.session = None
        self._task = None
        self._stop = None

    async def start(self, parameters, timeout):
        ready = asyncio.get_running_loop().create_future()
        self._stop = asyncio.Event()

        async def own_session():
            try:
                async with stdio_client(parameters) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        self.session = session
                        ready.set_result(session)
                        await self._stop.wait()
            except BaseException as exc:
                if not ready.done():
                    ready.set_exception(exc)
                else:
                    raise
            finally:
                self.session = None

        self._task = asyncio.create_task(own_session(), name='mcp-stdio-owner')
        try:
            return await asyncio.wait_for(asyncio.shield(ready), timeout=timeout)
        except BaseException:
            ready.cancel()
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            raise

    async def close(self):
        if self._task is None:
            return
        self._stop.set()
        try:
            await self._task
        finally:
            self._task = None
