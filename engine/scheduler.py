import asyncio
import contextlib
import inspect
import uuid
from asyncio import Task
from datetime import datetime
from functools import partial
from typing import Any, Coroutine, Callable
from uuid import UUID

from engine import EngineError

CREATED_STATE = 'CORO_CREATED'


class Scheduler:
    """
    Has the ability to schedule delayed coroutines/tasks.
    Should not block the main thread.
    """

    def __init__(self):
        pass

    def schedule_in(self, callback: Callable[[Any], Any], time: int | float, **kwargs: Any):
        asyncio.run(self._gather(callback, time, **kwargs))

    async def _gather(self, callback: Callable[[Any], Any], time: int | float, **kwargs: Any):
        coroutine: Coroutine[Any, Any, Any] = self._run_callback(callback, time, **kwargs)
        await asyncio.gather(coroutine, coroutine, coroutine)

    async def _run_callback(self, callback: Callable[[Any], Any], time: int | float, **kwargs: Any):
        await asyncio.sleep(delay=time)
        callback(**kwargs)
