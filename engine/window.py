import sys

import pygame
from pygame import Color, Surface
from pygame.time import Clock

import engine


class Resolution:
    """
    A basic class for storing a specific resolution and scalar.
    """

    def __init__(self, width: int, height: int, *, scalar: float = 1, other: 'Resolution | None' = None):
        self._width = width
        self._height = height
        self._scalar = scalar if not other else abs(self._width / other._width)

    @property
    def width(self) -> int:
        """
        Gets the width of the resolution, in pixels.

        :return: The width of the resolution, in pixels.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        Gets the height of the resolution, in pixels.

        :return: The height of the resolution, in pixels.
        """
        return self._height

    @property
    def scalar(self) -> float:
        """
        Gets an optional scalar of the resolution, in comparison to another.
        By default, this method will return 1 if not given an `other` in the constructor.

        :return: The optional scalar of the resolution, in comparison to another.
        """
        return self._scalar

    def as_tuple(self) -> tuple[int, int]:
        """
        Gets the width and height as a tuple, formatted (width, height).

        :return: The width and height as a tuple.
        """
        return self._width, self._height


class Window:

    def __init__(self, resolution: Resolution, *, background: Color = Color(0), title: str = 'PyGame', fps: int = 30):
        self._resolution = resolution
        self._background = background
        self._title = title
        self._fps = fps
        self._running = False
        self._surface = pygame.display.set_mode(size=resolution.as_tuple())
        self._clock = Clock()
        self._tick_count = 0

    def start(self) -> None:
        """
        Starts the game loop and opens the window.
        Manages events, entities, and updating the display.

        :return: None
        """
        pygame.display.set_caption(self._title)
        self._running = True

        while self._running:
            self._tick_count += 1
            self._clock.tick(self._fps)
            self._surface.fill(self._background)
            engine.event_handler.handle_events(pygame.event.get())
            engine.entity_handler.tick(self._tick_count)
            engine.entity_handler.draw(self._surface)
            pygame.display.flip()

        engine.entity_handler.clear()
        engine.event_handler.clear()
        pygame.quit()
        sys.exit()

    def stop(self) -> None:
        """
        Stops the game loop and subsequently the pygame window.

        :return: None
        """
        self._running = False

    @property
    def resolution(self) -> Resolution:
        return self._resolution

    @property
    def surface(self) -> Surface:
        return self._surface

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def running(self) -> bool:
        return self._running

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def background(self) -> Color:
        return self._background

    @background.setter
    def background(self, value: Color) -> None:
        self._background = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        pygame.display.set_caption(title=value)
