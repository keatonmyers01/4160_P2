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

        projectile = HealerProjectile(location=self.location.copy(), velocity=(0, 0), health=health,
                                      healing_rate=healing_rate, priority=20, detect_range=detect_range,
                                      life_span=life_span)
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


class HealerProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 health: int = 0,
                 healing_rate: int = 0,
                 detect_range: int = 0,
                 life_span: float = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._health = health
        self._healing_rate = healing_rate
        self._radius = 5
        self.color = (100, 100, 100)
        self.detect_range = detect_range
        self.target = None
        self.onTarget = False
        self._life_span = round(life_span * engine.window.fps)

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]):
        self._velocity = value

    def aquire_projectile_velocities(self, target: Entity, max_velocity: int) -> tuple[float, float]:
        orgin = self.location
        target_location = target.location
        x_distance = orgin.dist_x(target_location)
        y_distance = orgin.dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = distance_ratio * max_velocity
        y_velocity = (1 - distance_ratio) * max_velocity
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1

        return x_velocity, y_velocity

    def tick(self, tick_count: int) -> None:
        if self.target is None:
            towers = self.nearby_entities_type(self.detect_range, Tower)
            min_tower_health = 100000
            for tower in towers:
                if tower.heath < min_tower_health:
                    self.target = tower
                    ##min_tower_health = tower.health
        elif not self.onTarget:
            self.velocity = self.aquire_projectile_velocities(self.target, 5)
            self.location.add(self._velocity[0], self._velocity[1])
            collisions = self.nearby_entities_type(self._radius, Tower)
            if self.target in collisions:
                self.velocity = (0, 0)
                self.onTarget = True
        if self.onTarget:
            self.on_collide()

        if self._life_span <= 0:
            self.dispose()
        else:
            self._life_span -= 1

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self):
        ##self.target.heal(min(self._healing_rate, self._health))
        self._health -= self._healing_rate
        if self._health <= 0:
            self.dispose()
