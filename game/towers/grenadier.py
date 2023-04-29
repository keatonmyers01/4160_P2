import pygame
from pygame import Surface, Rect

import engine
from engine import EngineError
from engine.entity import Entity
from engine.location import Location
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType


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
        projectile = GrenadierProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage,
                                         priority=20, aoe_radius=aoe_radius)
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

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


class GrenadierProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0,
                 aoe_radius: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 6
        self.color = (50, 50, 50)
        self._aoe_radius = aoe_radius

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
            self.on_collide()

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self):
        enemies = self.nearby_entities_type(self._aoe_radius, Enemy)
        for enemy in enemies:
            enemy.damage(self._damage)
        self.dispose()
