from pygame import Rect, Surface

from engine.entity import Entity
from engine.errors import BadArgument
from game.tower import Tower
from game.texture import Texture


class Cell(Entity):

    def __init__(self, x: int, y: int, *, tower: Tower | None = None):
        super().__init__()
        self._x = x
        self._y = y
        self._tower = tower

    def tick(self, tick_count: int) -> None:
        if self._tower:
            self._tower.tick(tick_count)

    def draw(self, surface: Surface) -> None:
        if self._tower:
            self._tower.draw(surface)
        else:
            pass  # todo

    def bounds(self) -> Rect:
        return self._tower.bounds()

    @property
    def empty(self) -> bool:
        return self._tower is None

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y


class Grid(Entity):

    def __init__(self, w: int, h: int, *, core_at: tuple[int, int] | None = None):
        if w < 1 or h < 1:
            raise BadArgument('Given width or height less than 1.')
        self._w = w
        self._h = h
        self._cells: list[list[Cell]] = []

    def on_load(self) -> None:
        for i in range(self._w):
            for j in range(self._h):
                # todo: check if i, j at core_at and add core tower as arg
                cell = Cell(i, j)
                cell_bounds = cell.bounds()
                cell_loc = self.location.copy()
                cell_loc.add(x=(i * cell_bounds.w), y=(j * cell_bounds.h))
                cell.location = cell_loc

    def tick(self, tick_count: int) -> None:
        pass

    def draw(self, surface: Surface) -> None:
        pass

    def bounds(self) -> Rect:
        pass
