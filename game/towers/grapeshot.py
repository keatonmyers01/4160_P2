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
            projectile = GrapeShotProjectile(location=self.location.copy(), velocity=(dx, dy), damage=damage,
                                             priority=20 + i)
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


class GrapeShotProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 5
        self.color = (150, 150, 150)

    @property
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]):
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
