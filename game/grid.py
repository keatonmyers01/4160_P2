from typing import Callable, Union

from pygame import Rect, Surface

import engine
from engine.entity import Entity
from engine.errors import BadArgument
from engine.location import Location
from game.constants import CELL_SIZE
from game.tower import Tower
from game.towers.core import CoreTower


class Cell(Entity):

    def __init__(self, x: int, y: int, grid: 'Grid', *, tower: Tower | None = None):
        super().__init__()
        self._x = x
        self._y = y
        self._grid = grid
        self._tower = tower

    def tick(self, tick_count: int) -> None:
        if self._tower:
            self._tower.tick(tick_count)

    def draw(self, surface: Surface) -> None:
        if self._tower:
            self._tower.draw(surface)
        else:
            surface.fill((32, 32, 32), self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(CELL_SIZE[0], CELL_SIZE[1])

    @property
    def empty(self) -> bool:
        return self._tower is None

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def tower(self) -> Tower | None:
        return self._tower

    @tower.setter
    def tower(self, value: Tower | None) -> None:
        value.location = self.location.copy()
        self._tower = value
        if value:
            engine.entity_handler.register_entity(value)
            value.spawn()
        if not value and self._tower:
            self._tower.dispose()

    @property
    def cell_above(self) -> 'Cell | None':
        if self._y + 1 >= self._grid.height:
            return None
        return self._grid.cells[self._x][self._y + 1]

    @property
    def cell_left(self) -> 'Cell | None':
        if self._x - 1 < 0:
            return None
        return self._grid.cells[self._x - 1][self._y]

    @property
    def cell_right(self) -> 'Cell | None':
        if self._x + 1 >= self._grid.width:
            return None
        return self._grid.cells[self._x + 1][self._y]

    @property
    def cell_below(self) -> 'Cell | None':
        if self._y - 1 < 0:
            return None
        return self._grid.cells[self._x][self._y - 1]

    @Entity.location.setter
    def location(self, value: Union[Location, Callable[[Rect], Location]]) -> None:
        self._loc = value if isinstance(value, Location) else value(self.bounds())
        if self._tower:
            self._tower.location = value

    def _on_dispose(self) -> None:
        if self._tower:
            self._tower.dispose()


class Grid(Entity):

    def __init__(self, w: int, h: int, *, core_at: tuple[int, int] | None = None):
        super().__init__(priority=10)
        if w < 1 or h < 1:
            raise BadArgument('Given width or height less than 1.')
        self._w = w
        self._h = h
        self._cells: list[list[Cell]] = [[Cell(i, j, self) for j in range(self._h)] for i in range(self._w)]
        if core_at:
            self._cells[core_at[0]][core_at[1]].tower = CoreTower()

    def _on_load(self) -> None:
        for i in range(self._w):
            for j in range(self._h):
                cell = self._cells[i][j]
                cell_loc = self.location.copy()
                cell_loc.add(x=(i * CELL_SIZE[0]), y=(j * CELL_SIZE[1]))
                cell.location = cell_loc

    def tick(self, tick_count: int) -> None:
        for i in range(self._w):
            for j in range(self._h):
                self._cells[i][j].tick(tick_count)

    def draw(self, surface: Surface) -> None:
        for i in range(self._w):
            for j in range(self._h):
                self._cells[i][j].draw(surface)

    def bounds(self) -> Rect:
        return self.location.as_rect(CELL_SIZE[0] * self._w, CELL_SIZE[1] * self._h)

    @property
    def cells(self) -> list[list[Cell]]:
        return self._cells

    @property
    def width(self) -> int:
        return self._w

    @property
    def height(self) -> int:
        return self._h

    def get_cell_on_click(self, mouse_pos: tuple[int, int]) -> Cell | None:
        if not self.bounds().collidepoint(mouse_pos):
            return None
        col = int((mouse_pos[0] - self.location.x) // CELL_SIZE[0])
        row = int((mouse_pos[1] - self.location.y) // CELL_SIZE[1])
        return self._cells[col][row]

    def can_place_tower(self,
                        *,
                        coords: tuple[int, int] | None = None,
                        mouse_pos: tuple[int, int] | None = None) -> bool:
        cell: Cell | None = None
        if coords:
            cell = self._cells[coords[0]][coords[1]]
        elif mouse_pos:
            cell = self.get_cell_on_click(mouse_pos)
        if not cell:
            return False
        if not cell.empty:
            return False
        for c in [cell.cell_left, cell.cell_above, cell.cell_right, cell.cell_below]:
            if c.empty:
                continue
            return True
        return False

    def _on_dispose(self) -> None:
        for i in range(self._w):
            for j in range(self._h):
                self._cells[i][j].dispose()
