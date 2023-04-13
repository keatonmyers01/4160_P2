from abc import abstractmethod
from enum import Enum

import pygame
from pygame import Surface, Rect

from engine.entity import Entity
from game.texture import Texture


class EntityTargetType(Enum):

    ENEMY = 0,
    PLAYER = 1,
    TOWER = 2,
    FIELD = 3


class TowerStage(Enum):

    STAGE_1 = 1,
    STAGE_2 = 2,
    STAGE_3 = 3


class Tower(Entity):

    # this is an abstract class, so you'll need to create subclasses that extend Tower

    def __init__(self):
        self.health = self.starting_health()
        self.on_cooldown = False
        pass

    def tick(self, tick_count: int) -> None:

        pass

    @abstractmethod
    def regeneration_rate(self) -> int:
        """
        The amount of regeneration per second.
        :return:
        """
        pass

    @abstractmethod
    def starting_health(self) -> int:
        """
        The amount of health that a tower spawns with.
        :return:
        """
        pass

    @abstractmethod
    def entity_target(self) -> EntityTargetType:
        """
        The type of Entity that the tower will target.
        :return:
        """
        pass

    @abstractmethod
    def spawn_cost(self) -> int:
        """
        The amount of currency that the tower requires in order to spawn.
        :return:
        """
        pass

    @abstractmethod
    def ability_cooldown(self) -> float:
        """
        The amount of time, in seconds, to wait until the tower can use its ability.
        :return:
        """
        pass

    @abstractmethod
    def perform_ability(self) -> bool:
        pass

    def cancel_tasks(self) -> None:
        pass


class CoreTower(Tower):

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, (20, 20))

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def bounds(self) -> Rect:
        return self.location.as_rect(20, 20)

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 500

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def spawn_cost(self) -> int:
        return 0

    def ability_cooldown(self) -> float:
        return 1

    def perform_ability(self) -> bool:
        return False
