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
from game.projectile import ArcherProjectile, HealerProjectile
from game.projectile import GrapeShotProjectile
from game.projectile import ShrapnelProjectile
from game.projectile import MinefieldProjectile
from game.projectile import GrenadierProjectile
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
        The type of Entity that the tower will target.
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
        The amount of health that a tower spawns with.
        :return:
        """
        return self._starting_health

    def build_cost(self) -> int:
        """
        The amount of currency that the tower requires in order to build.
        :return:
        """
        return self._building_cost

    def ability_cooldown(self) -> float:
        """
        The amount of time, in seconds, to wait until the tower can use its ability.
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

    def aquire_projectile_velocities(self, target: Entity, max_velocity: int) -> tuple[int, int]:
        orgin = self.location
        target_location = target.location
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

        return x_velocity, y_velocity


class CoreTower(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 40
                max_velocity = 8
            case TowerStage.STAGE_2:
                damage = 50
                max_velocity = 8
            case TowerStage.STAGE_3:
                damage = 80
                max_velocity = 8
            case _:
                raise EngineError()

        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage, priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

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
        match self.stage:
            case TowerStage.STAGE_1:
                health = 30
                healing_rate = 10
                detect_range = 100
                life_span = 10
            case TowerStage.STAGE_2:
                health = 60
                healing_rate = 15
                detect_range = 150
                life_span = 10
            case TowerStage.STAGE_3:
                health = 100
                healing_rate = 20
                detect_range = 200
                life_span = 10
            case _:
                raise EngineError()

        projectile = HealerProjectile(location=self.location.copy(), velocity=(0,0), health=health, healing_rate=healing_rate, priority=20, detect_range=detect_range, life_span=life_span)
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
        return 3

    def starting_health(self) -> int:
        return 200

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.NONE

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
                damage = 45
                max_velocity = 5
            case TowerStage.STAGE_3:
                damage = 60
                max_velocity = 5
            case _:
                raise EngineError()

        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage, priority=20)
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
        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        for i in range(projectile_count):
            dx = projectile_velocity[0] + random.randint(-1, 1)
            dy = projectile_velocity[1] + random.randint(-1, 1)
            projectile = GrapeShotProjectile(location=self.location.copy(), velocity=(dx, dy), damage=damage, priority=20+i)
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
                max_velocity = 3
                damage = 15
                secondary_count = 6
            case TowerStage.STAGE_2:
                max_velocity = 3
                damage = 20
                secondary_count = 10
            case TowerStage.STAGE_3:
                max_velocity = 3
                damage = 30
                secondary_count = 15
            case _:
                raise EngineError('L')
        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        projectile = ShrapnelProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage, priority=20, secondary_count=secondary_count)
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
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 150
            case TowerStage.STAGE_2:
                damage = 300
            case TowerStage.STAGE_3:
                damage = 600
            case _:
                raise EngineError('L')
        args[0].damage(damage)

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
        return 400

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class Minefield(Tower):

    def _on_ability(self, *args: Enemy | None) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 30
                max_velocity = 5
                lifespan = 5
                aoe_radius = 100
            case TowerStage.STAGE_2:
                damage = 40
                max_velocity = 5
                lifespan = 7
                aoe_radius = 150
            case TowerStage.STAGE_3:
                damage = 60
                max_velocity = 5
                lifespan = 10
                aoe_radius = 250
            case _:
                raise EngineError()
        velocity_seed = random.randint(0, max_velocity)
        x_mod = 1
        y_mod = 1
        if random.randint(0, 1):
            x_mod *= -1
        if random.randint(0, 1):
            y_mod *= -1
        projectile_velocity = (velocity_seed * x_mod, (5 - velocity_seed) * y_mod)
        projectile = MinefieldProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage, priority=20, aoe_radius=aoe_radius, life_span=lifespan)
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
        return EntityTargetType.NONE

    def build_cost(self) -> int:
        return 30

    def ability_cooldown(self) -> float:
        return 1

    def area_of_effect(self) -> int:
        return 200

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass


class Grenadier(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 30
                max_velocity = 5
                aoe_radius = 150
            case TowerStage.STAGE_2:
                damage = 40
                max_velocity = 5
                aoe_radius = 150
            case TowerStage.STAGE_3:
                damage = 60
                max_velocity = 5
                aoe_radius = 150
            case _:
                raise EngineError()
        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        projectile = GrenadierProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage, priority=20, aoe_radius = aoe_radius)
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


class Leach(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 40
                radius = 75
                healing = 5
            case TowerStage.STAGE_2:
                damage = 65
                radius = 85
                healing = 7
            case TowerStage.STAGE_3:
                damage = 90
                radius = 100
                healing = 10
            case _:
                raise EngineError('L')
        targets = args[0].nearby_entities_type(radius, Enemy)

        for target in targets:
            target.damage(damage)
            #TODO add in the healing

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
        return 4

    def area_of_effect(self) -> int:
        return 300

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass
