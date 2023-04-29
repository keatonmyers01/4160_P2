from abc import abstractmethod
from enum import Enum
from threading import Timer

from pygame import Rect

import engine
from engine.entity import Entity, LivingEntity
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


class Tower(LivingEntity):

    # this is an abstract class, so you'll need to create subclasses that extend Tower

    def __init__(self, *, stage: TowerStage = TowerStage.STAGE_1):
        super().__init__()
        self.on_cooldown = True
        self._regeneration_rate = 0
        self._starting_health = 0
        self._building_cost = 0
        self._ability_cooldown = 0
        self._area_of_effect = 0
        self.ability_timer = Timer(self.ability_cooldown(), self.perform_ability)
        self._stage = stage

    def __del__(self):
        if self.ability_timer.is_alive():
            self.ability_timer.cancel()
            self.ability_timer.join(1)

    def _on_load(self) -> None:
        self.ability_timer.start()

    def _on_dispose(self) -> None:
        self.__del__()

    def tick(self, tick_count: int) -> None:
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
            self._on_ability(*targets)
            self.on_cooldown = True
            self.ability_timer = Timer(self.ability_cooldown(), self.perform_ability)
            self.ability_timer.start()
            return
        self.on_cooldown = False

    def aquire_projectile_velocities(self, target: Entity, max_velocity: int) -> tuple[float, float]:
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
