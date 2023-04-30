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
import random


class Archer(Tower):

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)
        self._building_cost = 30
        self._max_velocity = 5

        self._damage = 20
        self._regeneration_rate = 0
        self._starting_health = 100
        self._max_health = 200
        self._ability_cooldown = 1
        self._health = self._starting_health
        self._upgrade_cost = 30
        self._area_of_effect = 150

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = self.aquire_projectile_velocities(random.choice(args), self._max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=self._damage,
                                      priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return self._regeneration_rate

    def starting_health(self) -> int:
        return self._starting_health

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return self._building_cost

    def ability_cooldown(self) -> float:
        return self._ability_cooldown

    def area_of_effect(self) -> int:
        return self._area_of_effect

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 30
                self._max_health = 300
                self._health = 300
                self._area_of_effect = 200
                self._regeneration_rate = 1
                self._upgrade_cost = 70
                self._ability_cooldown = 0.8
            case TowerStage.STAGE_3:
                self._damage = 45
                self._max_health = 450
                self._health = 450
                self._area_of_effect = 250
                self._regeneration_rate = 1
                self._ability_cooldown = 0.5
            case _:
                raise EngineError()

    @property
    def max_health(self) -> int:
        return 200

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


class ArcherProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 10
        self.color = (100, 100, 100)

    @property
    def velocity(self) -> tuple[float, float]:
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
