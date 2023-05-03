from abc import abstractmethod
from enum import Enum
from threading import Timer

from pygame import Rect

import engine
from engine.entity import Entity
from engine.sprite import Sprite
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.player import Player


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


def aquire_projectile_velocities(self: Entity, target: Entity, max_velocity: int) -> tuple[float, float]:
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
