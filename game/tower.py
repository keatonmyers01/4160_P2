from abc import abstractmethod
from enum import Enum
from threading import Timer
from uuid import UUID

import pygame
from pygame import Surface, Rect

import engine
from engine.entity import Entity
from game.enemy import Enemy
from game.player import Player
from game.texture import Texture


class EntityTargetType(Enum):

    ENEMY = 0,
    PLAYER = 1,
    TOWER = 2,
    NONE = 3


class TowerStage(Enum):

    STAGE_1 = 1,
    STAGE_2 = 2,
    STAGE_3 = 3


class Tower(Entity):

    # this is an abstract class, so you'll need to create subclasses that extend Tower

    def __init__(self):
        super().__init__()
        self.on_cooldown = True
        self.ability_timer: Timer = Timer(self.ability_cooldown(), self.perform_ability)
        self._tasks: list[UUID] = []

    def __del__(self):
        if self.ability_timer.is_alive():
            self.ability_timer.cancel()
            self.ability_timer.join(1)

    def _on_load(self) -> None:
        print('Loading tower')
        self.ability_timer.start()

    def _on_dispose(self) -> None:
        self.__del__()

    def tick(self, tick_count: int) -> None:
        if not self.on_cooldown:
            self.perform_ability()

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
    def _on_ability(self, *args: Entity) -> None:
        pass

    def area_of_effect(self) -> int:
        return 0

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

    def _cancel_tasks(self) -> None:
        pass

    def _add_task(self, uuid: UUID) -> None:
        self._tasks.append(uuid)


class CoreTower(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        print('Core tower ability')
        for entity in args:
            entity.damage(50)

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, (20, 20))

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

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

    def area_of_effect(self) -> int:
        return 100
