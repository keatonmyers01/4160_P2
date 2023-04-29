import random

import pygame
from pygame import Surface, Rect

import engine
from engine import EngineError
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType


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
        projectile = ShrapnelProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage,
                                        priority=20, secondary_count=secondary_count)
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

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


class ShrapnelProjectileSecondary(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 4
        self.color = (175, 125, 175)

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]):
        self._velocity = value

    def tick(self, tick_count: int) -> None:
        self.location.add(self._velocity[0], self._velocity[1])
        collisions = self.nearby_entities_type(self._radius, Enemy)
        if len(collisions) > 0:
            self.on_collide(collisions[0])

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self, entity: LivingEntity):
        entity.damage(self._damage)
        self.dispose()


class ShrapnelProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0,
                 secondary_count: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 3
        self._damage = damage
        self._radius = 15
        self.color = (125, 125, 125)
        self._travel = 250
        self._travel_dist = velocity[0] + velocity[1]
        self._secondary_count = secondary_count
        self._secondary_damage = int(damage / 2)

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]):
        self._velocity = value

    def tick(self, tick_count: int) -> None:
        self.location.add(self._velocity[0], self._velocity[1])
        collisions = self.nearby_entities_type(self._radius, Enemy)
        if len(collisions) > 0:
            self.on_collide(collisions[0])
        self._travel -= self._travel_dist
        if self._travel <= 0:
            self.on_collide(None)

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self, entity: LivingEntity | None):
        if entity is not None:
            entity.damage(self._damage)

        for i in range(self._secondary_count):
            projectile_velocity = (0, 0)
            while projectile_velocity == (0, 0):
                projectile_velocity = (random.uniform(-5, 5), random.uniform(-5, 5))

            projectile = ShrapnelProjectileSecondary(location=self.location.copy(),
                                                     velocity=projectile_velocity,
                                                     damage=self._secondary_damage,
                                                     priority=20 + i)
            engine.entity_handler.register_entity(projectile)
            projectile.spawn()
        self.dispose()
