import random
from abc import abstractmethod
from enum import Enum
from threading import Timer

import pygame
from pygame import Surface, Rect

import engine
from engine import EngineError
from engine.entity import Entity
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.player import Player
from game.projectile import ArcherProjectile
from game.projectile import GrapeShotProjectile
from game.projectile import ShrapnelProjectile
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

    def next(self) -> 'TowerStage | None':
        match self:
            case TowerStage.STAGE_1:
                return TowerStage.STAGE_2
            case TowerStage.STAGE_2:
                return TowerStage.STAGE_3
            case _:
                return None


class Tower(Entity):

    # this is an abstract class, so you'll need to create subclasses that extend Tower

    def __init__(self, *, stage: TowerStage = TowerStage.STAGE_1):
        super().__init__()
        self.on_cooldown = True
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

    @property
    def stage(self) -> TowerStage:
        return self._stage

    @stage.setter
    def stage(self, value: TowerStage) -> None:
        self._stage = value
        self._on_upgrade(stage=value)

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
    def build_cost(self) -> int:
        """
        The amount of currency that the tower requires in order to build.
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

    @abstractmethod
    def _on_upgrade(self, stage: TowerStage) -> None:
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


class CoreTower(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        args[0].damage(50)

    def __init__(self):
        super().__init__()
        self._texture = pygame.image.load(Texture.CORE_TOWER.value)
        self._texture = pygame.transform.scale(self._texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self._texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 1

    def starting_health(self) -> int:
        return 500

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 0

    def ability_cooldown(self) -> float:
        return 1

    def area_of_effect(self) -> int:
        return 100

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class Healer(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        pass

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 3

    def starting_health(self) -> int:
        return 200

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.TOWER

    def build_cost(self) -> int:
        return 30

    def ability_cooldown(self) -> float:
        return 0

    def area_of_effect(self) -> int:
        return 1

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class Archer(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 30
                max_velocity = 5
            case TowerStage.STAGE_2:
                damage = 40
                max_velocity = 5
            case TowerStage.STAGE_3:
                damage = 60
                max_velocity = 5
            case _:
                raise EngineError()
        orgin = self.location.copy()
        target_location = args[0].location
        x_distance = orgin.dist_x(target_location)
        y_distance = orgin.dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = round(distance_ratio * max_velocity)
        y_velocity = round((1 - distance_ratio) * max_velocity)
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1
        projectile_velocity = (x_velocity, y_velocity)
        projectile = ArcherProjectile(location=orgin, velocity=projectile_velocity, damage=damage, priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 250

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 30

    def ability_cooldown(self) -> float:
        return 1

    def area_of_effect(self) -> int:
        return 200

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class GrapeShot(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                projectile_count = 4
                max_velocity = 5
                damage = 20
            case TowerStage.STAGE_2:
                projectile_count = 6
                max_velocity = 5
                damage = 30
            case TowerStage.STAGE_3:
                projectile_count = 10
                max_velocity = 5
                damage = 45
            case _:
                raise EngineError('L')
        orgin = self.location
        target_location = args[0].location
        x_distance = orgin.dist_x(target_location)
        y_distance = orgin.dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = round(distance_ratio * max_velocity)
        y_velocity = round((1 - distance_ratio) * max_velocity)
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1

        for i in range(projectile_count):
            dx = x_velocity + random.randint(-1, 1)
            dy = y_velocity + random.randint(-1, 1)
            print(f'{dx}, {dy}')
            projectile = GrapeShotProjectile(location=orgin.copy(), velocity=(dx, dy), damage=damage, priority=20+i)
            engine.entity_handler.register_entity(projectile)
            projectile.spawn()

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 350

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 50

    def ability_cooldown(self) -> float:
        return 1.5

    def area_of_effect(self) -> int:
        return 250

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class ShrapnelCannon(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                max_volocity = 3
                damage = 15
                secondary_count = 6
            case TowerStage.STAGE_2:
                max_volocity = 3
                damage = 20
                secondary_count = 10
            case TowerStage.STAGE_3:
                max_volocity = 3
                damage = 30
                secondary_count = 15
            case _:
                raise EngineError('L')
        orgin = self.location.copy()
        target_location = args[0].location
        x_distance = orgin.dist_x(target_location)
        y_distance = orgin.dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = round(distance_ratio * max_volocity)
        y_velocity = round((1 - distance_ratio) * max_volocity)
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1

        projectile_velocity = (x_velocity, y_velocity)
        projectile = ShrapnelProjectile(location=orgin, velocity=projectile_velocity, damage=damage, priority=20, secondary_count=secondary_count)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 350

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 40

    def ability_cooldown(self) -> float:
        return 2

    def area_of_effect(self) -> int:
        return 250

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class Sniper(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        args[0].damage(150)

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 250

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 40

    def ability_cooldown(self) -> float:
        return 3

    def area_of_effect(self) -> int:
        return 150

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass
