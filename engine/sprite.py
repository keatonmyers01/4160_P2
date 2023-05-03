from abc import abstractmethod
from enum import Enum
from typing import TypeVar, Callable

import pygame.image
from pygame import Rect, Surface

from engine import EngineError
from engine.entity import LivingEntity

SPRITE_STATE = TypeVar('SPRITE_STATE', bound=Enum)


class StateChange:

    def __init__(self, before: SPRITE_STATE, callback: Callable[[], None], loops: int):
        self._before = before
        self._callback = callback
        self._loops = loops

    def loop(self, sprite: 'Sprite') -> None:
        self._loops -= 1
        if self._loops == 0:
            self._callback()
            sprite.state = self._before


class Sprite(LivingEntity):

    def __init__(self,
                 default_state: SPRITE_STATE,
                 *,
                 ticks_per_frame: int = 1,
                 scalar: float = 1,
                 bound_to_screen: bool = False,
                 health_bar: bool = False,
                 priority: int = 0):
        super().__init__(priority=priority, bound_to_screen=bound_to_screen, health_bar=health_bar)
        self._state = default_state
        self._animations: dict[SPRITE_STATE, list[Surface]] = {}
        self._states: dict[SPRITE_STATE, tuple[str, int]] = {}
        self._state_change: StateChange | None = None
        self._scalar = scalar
        self._frame_index = 0
        self._tick_index = ticks_per_frame
        self._ticks_per_frame = ticks_per_frame

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)
        self._tick_index -= 1
        if self._tick_index == 0:
            if self._frame_index < len(self._animations[self._state]) - 1:
                self._frame_index += 1
            else:
                self._frame_index = 0
                if self._state_change:
                    self._state_change.loop(self)
            self._tick_index = self._ticks_per_frame

    def draw(self, surface: Surface) -> None:
        super().draw(surface)
        surface.blit(self._animations[self._state][self._frame_index], self.location.as_tuple())

    def bounds(self) -> Rect:
        state_image = self._animations[self._state][self._frame_index]
        return self.location.as_rect(state_image.get_width(), state_image.get_height())

    def spawn(self) -> None:
        super().spawn()
        if len(self._animations) == 0:
            raise EngineError('Sprite spawned with 0 animations.')

    def add_state(self, state: SPRITE_STATE, path: str, frame_count: int) -> None:
        """
        Adds the given state with the given path and frame count to the sprite.

        :param state: The sprite state.
        :param path: The path of the animation.
        :param frame_count: The amount of frames in the sprite state/animation.
        :return: None
        """
        if state in self._states:
            raise EngineError(f'The sprite state {state.name} has already been set.')
        images = []
        for i in range(frame_count):
            image = pygame.image.load(f'{path}/{state.value}/{i}.png')
            new_width = image.get_width() * self._scalar
            new_height = image.get_height() * self._scalar
            image = pygame.transform.scale(image, (new_width, new_height))
            images.append(image)
        self._animations[state] = images
        self._states[state] = (path, frame_count)

    def queue_state(self, state: SPRITE_STATE, callback: Callable[[], None], *, loops: int = 1) -> None:
        """
        Sets the given sprite state and waits until the given
        number of loops has passed until calling the given callback.

        The sprite will then swap back to the sprite state it was before being played.

        :param state: The state to set.
        :param callback: The callback to run after the animation finishes.
        :param loops: The number of loops of the animation to play.
        :return: None
        """
        if loops < 1:
            raise EngineError('Cannot queue state change with loops < 1.')
        self._state_change = StateChange(self._state, callback=callback, loops=loops)
        self._state = state
        self._frame_index = 0

    @property
    def state(self) -> SPRITE_STATE:
        return self._state

    @state.setter
    def state(self, value: SPRITE_STATE) -> None:
        self._state = value
        self._frame_index = 0
        if self._state_change:
            self._state_change = None

    @property
    @abstractmethod
    def max_health(self) -> int:
        pass

    @abstractmethod
    def _on_damage(self) -> None:
        pass

    @abstractmethod
    def _on_heal(self) -> None:
        pass

    @abstractmethod
    def _on_death(self) -> None:
        pass
