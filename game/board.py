from abc import abstractmethod
from enum import Enum
from random import randint, choice
from threading import Timer
from typing import Callable, Union

import pygame.image
from pygame import Rect, Surface

import engine
from engine.entity import Entity, LivingEntity
from engine.errors import BadArgument
from engine.location import Location
from engine.sprite import Sprite
from game.constants import CELL_SIZE
from game.player import Player
from game.texture import Texture


class Cell(Entity):

    def __init__(self, x: int, y: int, grid: 'Grid', *, tower: 'Tower | None' = None):
        super().__init__()
        self._x = x
        self._y = y
        self._grid = grid
        self._tower = tower
        texture = pygame.image.load(Texture.CELL.value)
        self._texture = pygame.transform.scale(texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        if self._tower:
            self._tower.tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self._texture, self.location.as_tuple())
        if self._tower:
            self._tower.draw(surface)

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
    def tower(self) -> 'Tower | None':
        return self._tower

    @tower.setter
    def tower(self, value: 'Tower | None') -> None:
        value.location = self.location.copy()
        self._tower = value
        value.cell = self
        if value:
            engine.entity_handler.register_entity(value)
            value.spawn()
        if not value and self._tower:
            self._tower.dispose()
            self._tower.cell = None

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


TEXTURE_PATH = 'game/asset/tower'


class EntityTargetType(Enum):
    ENEMY = 0,
    PLAYER = 1,
    TOWER = 2,
    NONE = 3


class TowerStage(Enum):
    STAGE_1 = 1,
    STAGE_2 = 2,
    STAGE_3 = 3

    def next(self) -> 'TowerStage | None':
        match self:
            case TowerStage.STAGE_1:
                return TowerStage.STAGE_2
            case TowerStage.STAGE_2:
                return TowerStage.STAGE_3
            case _:
                return None


class TowerState(Enum):

    IDLE = 'idle'
    PERFORMING_ABILITY = 'anim'


class Tower(Sprite):

    # this is an abstract class, so you'll need to create subclasses that extend Tower

    def __init__(self,
                 *,
                 scalar: float = 1,
                 ticks_per_frame: int = 1,
                 stage: TowerStage = TowerStage.STAGE_1):
        super().__init__(TowerState.IDLE, scalar=scalar, ticks_per_frame=ticks_per_frame, priority=30, health_bar=True)
        self._cell: Cell | None = None
        self.on_cooldown = True
        self._regeneration_rate = 0
        self._starting_health = 0
        self._building_cost = 0
        self._ability_cooldown = 0
        self._area_of_effect = 0
        self._ability_timer = Timer(self.ability_cooldown(), self.perform_ability)
        self._stage = stage

    def __del__(self):
        if self._ability_timer.is_alive():
            self._ability_timer.cancel()
            self._ability_timer.join(1)

    def _on_load(self) -> None:
        self._ability_timer.start()

    def _on_dispose(self) -> None:
        self.__del__()

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)
        if not self.on_cooldown:
            self.perform_ability()

    def bounds(self) -> Rect:
        w, h = CELL_SIZE
        return self.location.as_rect(w, h)

    @abstractmethod
    def _on_ability(self, *args: Entity) -> None:
        pass

    @abstractmethod
    def _on_upgrade(self, stage: TowerStage) -> None:
        pass

    @abstractmethod
    def entity_target(self) -> EntityTargetType:
        """
        The type of Entity that the towers will target.
        :return:
        """
        pass

    @property
    def stage(self) -> TowerStage:
        return self._stage

    @stage.setter
    def stage(self, value: TowerStage) -> None:
        self._stage = value
        self._on_upgrade(value)

    @property
    def cell(self) -> Cell | None:
        return self._cell

    @cell.setter
    def cell(self, value: Cell | None) -> None:
        self._cell = value

    @property
    def tower_above(self) -> 'Tower | None':
        if not self._cell:
            return None
        return self._cell.cell_above.tower

    @property
    def tower_left(self) -> 'Tower | None':
        if not self._cell:
            return None
        return self._cell.cell_left.tower

    @property
    def tower_right(self) -> 'Tower | None':
        if not self._cell:
            return None
        return self._cell.cell_right.tower
    
    @property
    def tower_below(self) -> 'Tower | None':
        if not self._cell:
            return None
        return self._cell.cell_below.tower

    def regeneration_rate(self) -> int:
        """
        The amount of regeneration per second.
        :return:
        """
        return self._regeneration_rate

    def starting_health(self) -> int:
        """
        The amount of health that a towers spawns with.
        :return:
        """
        return self._starting_health

    def build_cost(self) -> int:
        """
        The amount of currency that the towers requires in order to build.
        :return:
        """
        return self._building_cost

    def ability_cooldown(self) -> float:
        """
        The amount of time, in seconds, to wait until the towers can use its ability.
        :return:
        """
        return self._ability_cooldown

    def area_of_effect(self) -> int:
        return self._area_of_effect

    def perform_ability(self) -> None:
        targets: list[Entity] = []
        match self.entity_target():
            case EntityTargetType.ENEMY:
                targets = self.nearby_entities_type(self.area_of_effect(), Enemy)
            case EntityTargetType.TOWER:
                targets = self.nearby_entities_type(self.area_of_effect(), Tower)
            case EntityTargetType.PLAYER:
                targets = engine.entity_handler.get_entities(Player)
        if len(targets) > 0 or self.entity_target() is EntityTargetType.NONE:
            self.queue_state(TowerState.PERFORMING_ABILITY, self._post_ability)
            self._on_ability(*targets)
            self.on_cooldown = True
            return
        self.on_cooldown = False

    def _post_ability(self) -> None:
        """
        Private method used to reset the ability timer of the tower after their ability has been performed.
        Used due to having to wait for the full animation to play out before resetting the timer.

        :return: None
        """
        self._ability_timer = Timer(self.ability_cooldown(), self.perform_ability)
        self._ability_timer.start()


def calculate_projectile_vel(self: Entity, target: Entity, max_velocity: int) -> tuple[float, float]:
    orgin = self.location
    target_location = target.location
    x_distance = orgin.directional_dist_x(target_location)
    y_distance = orgin.directional_dist_y(target_location)
    total_distance = abs(y_distance) + abs(x_distance)
    distance_ratio = abs(x_distance / total_distance)
    x_velocity = distance_ratio * max_velocity
    y_velocity = (1 - distance_ratio) * max_velocity
    if x_distance < 0:
        x_velocity *= -1
    if y_distance < 0:
        y_velocity *= -1
    return x_velocity, y_velocity


class EnemyState(Enum):

    EXISTING = 'enemy'


class Enemy(Sprite):

    def __init__(self, mouse_pos: tuple[int, int]):
        super().__init__(EnemyState.EXISTING, priority=10, health_bar=True)
        self.add_state(EnemyState.EXISTING, 'game/asset', 6)
        self.location = Location()
        self.location.add(mouse_pos[0], mouse_pos[1])
        self.on_cooldown = True
        self._type: bool = bool(randint(0, 1))
        self._target_timer: int = 0
        self.aquired_target: bool = False
        self.target: LivingEntity | None = None
        self._velocity: tuple[float, float] = (0, 0)
        self.max_velocity: int = 2
        self.on_target: bool = False
        self.damage: int = 25
        self.ability_cooldown: int = 0
        self._ability_timer = Timer(self.ability_cooldown, self.perform_ability)

    def calculate_travel_velocity(self) -> tuple[float, float]:
        orgin = self.location.copy()
        target_location = self.target.location.copy()
        x_distance = orgin.directional_dist_x(target_location)
        y_distance = orgin.directional_dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = distance_ratio * self.max_velocity
        y_velocity = (1 - distance_ratio) * self.max_velocity
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1
        return x_velocity, y_velocity

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)
        # reestablish a target every second
        if (self._target_timer % 30 and not self.on_target) or self._target_timer == 0:
            target_range = 1
            if self.aquired_target:
                search_factor = 20
            else:
                search_factor = 300
            targets = self.nearby_entities_type(target_range * search_factor, Tower)
            while len(targets) <= 0:
                targets = self.nearby_entities_type(target_range * search_factor, Tower)
                target_range += 1
                if target_range == 6:
                    return
            self.target = choice(targets)
            self.aquired_target = True
        self._target_timer += 1

        # move towards target
        self.location.add(self._velocity[0], self._velocity[1])

        # detect if the entity is on target
        if not self.on_target:
            self._velocity = self.calculate_travel_velocity()
            collisions = self.nearby_entities_type(10, Tower)
            if self.target in collisions:
                self._velocity = (0, 0)
                self.on_target = True

        if not self.on_cooldown:
            self.perform_ability()

    def bounds(self) -> Rect:
        return self.location.as_rect(10, 10)

    def ability_cooldown(self) -> float:
        return 0.5

    def _on_ability(self):
        print("on ability")
        self.target.damage(self.damage)

    def perform_ability(self) -> None:
        print("performing ability")
        if self.on_target:
            self._on_ability()
            self.on_cooldown = True
        else:
            self.on_cooldown = False

    @property
    def max_health(self) -> int:
        return 200

    def _on_dispose(self) -> None:
        print(f"I am dying {self.location}")

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


CORE_TEXTURE_PATH = f'{TEXTURE_PATH}/core'


class CoreTower(Tower):

    def __init__(self):
        super().__init__(scalar=0.6, ticks_per_frame=4)
        self.add_state(TowerState.IDLE, CORE_TEXTURE_PATH, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, CORE_TEXTURE_PATH, 8)
        self._building_cost = 0
        self._max_velocity = 8
        self._damage = 40
        self._regeneration_rate = 1
        self._max_health = 1000
        self._ability_cooldown = 1
        self._upgrade_cost = 100
        self._area_of_effect = 150

    def _on_ability(self, *args: Enemy) -> None:
        # todo
        pass

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 50
                self._max_health = 1500
                self._health = 1500
                self._area_of_effect = 150
                self._regeneration_rate = 2
                self._upgrade_cost = 250
            case TowerStage.STAGE_3:
                self._damage = 80
                self._max_health = 2500
                self._health = 2500
                self._area_of_effect = 250
                self._regeneration_rate = 3

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
