import asyncio
import contextlib
import inspect
import uuid
from asyncio import Task
from datetime import datetime
from functools import partial
from typing import Any, Coroutine
from uuid import UUID

from engine import EngineError

CREATED_STATE = 'CORO_CREATED'


class Scheduler:
    """
    Has the ability to schedule delayed coroutines/tasks.
    Should not block the main thread.
    """

    def __init__(self):
        self._scheduled_tasks: dict[UUID, Task[Any]] = {}

    def __contains__(self, item: UUID) -> bool:
        return item in self._scheduled_tasks

    def schedule_at(self, callback: Coroutine[Any, Any, Any], *, time: datetime) -> UUID:
        """
        Schedules the given callback to be executed at the given time.

        :param callback: The coroutine to call at the given time.
        :param time: The time to execute the coroutine.
        :return: The UUID of the scheduled task.
        """
        delay_time = (time - datetime.utcnow()).total_seconds()
        if delay_time < 0:
            raise EngineError('Given negative time.')
        if callback is None:
            raise EngineError('Given callback is None.')
        return self._schedule(delay_time, callback)

    def schedule_in(self, callback: Coroutine[Any, Any, Any], *, time: int | float) -> UUID:
        """
        Schedules the given callback to be executed `time` seconds from the current time.

        :param callback: The coroutine to call in `time` seconds.
        :param time: The number of seconds to wait before executing the coroutine.
        :return: The UUID of the scheduled task.
        """
        if callback is None:
            raise EngineError('Given callback is None.')
        if time < 0:
            raise EngineError('Given negative time.')
        return self._schedule(time, callback)

    def get_task(self, task_id: UUID) -> Task[Any] | None:
        """
        Gets the task that corellates to the given task_id.
        If a task with the given UUID does not exist, None is returned.

        :param task_id: The UUID of the task, given upon scheduling.
        :return: The task that corellates to the given task_id or None if a task with the given UUID does not exist.
        """
        if task_id in self._scheduled_tasks:
            return self._scheduled_tasks[task_id]
        return None

    def cancel(self, task_id: UUID) -> None:
        """
        Cancels the task that corellates to the given task_id, if it exists and has not already been executed.

        :param task_id: The UUID of the task, given upon scheduling.
        :return: None
        """
        if task_id in self._scheduled_tasks:
            self._scheduled_tasks[task_id].cancel()
            self._scheduled_tasks.pop(task_id)

    def _schedule(self, time: float | int, callback: Coroutine[Any, Any, Any]) -> UUID:
        task_id = uuid.uuid4()
        delayed_callback = self._delayed_callback(time, callback)
        task = asyncio.create_task(delayed_callback)
        task.add_done_callback(partial(self._end_scheduled_task, task_id))
        self._scheduled_tasks[task_id] = task
        return task_id

    def _end_scheduled_task(self, task_id: UUID, callback: Coroutine[Any, Any, Any]) -> None:
        if task_id in self._scheduled_tasks:
            self._scheduled_tasks.pop(task_id)
        with contextlib.suppress(asyncio.CancelledError):
            if exception := callback.exception():
                raise exception

    async def _delayed_callback(self, delay: float | int, callback: Coroutine[Any, Any, Any]) -> None:
        try:
            await asyncio.sleep(delay)
            await asyncio.shield(callback)
        finally:
            if inspect.getcoroutinestate(callback) == CREATED_STATE:
                callback.close()
