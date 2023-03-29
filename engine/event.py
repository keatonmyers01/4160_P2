from typing import Callable

import pygame
from pygame.event import Event


class EventHandler:
    """
    Handles events sent to the window by PyGame.
    """

    def __init__(self):
        self._events: dict[int, list[Callable[[Event], None]]] = {}

    def register(self, event_id: int, callback: Callable[[Event], None]) -> None:
        """
        Registers a new event with the given event_id and callback.

        :param event_id: The ID of the event.
        :param callback: The callback to call when the given event_id is triggered.
        :return: None.
        """
        callbacks = self._events[event_id] if event_id in self._events else []
        callbacks.append(callback)
        self._events[event_id] = callbacks

    def handle_events(self, events: list[Event]) -> None:
        """
        Called by the window to disperse all the events collecting since last tick.

        :param events: The list of events to handle.
        :return: None.
        """
        for event in events:
            if callbacks := self._events.get(event.type, None):
                for callback in callbacks:
                    callback(event)

    def clear(self) -> None:
        """
        Clears all the registered events.

        :return: None.
        """
        self._events.clear()


def new_event() -> int:
    new_id = new_event.counter
    new_event.counter += 1
    return new_id


new_event.counter = pygame.USEREVENT
