import pygame
from pygame import Surface, Rect

import engine
from engine.entity import Entity
from engine.location import Location
from game.board import Enemy, EntityTargetType, Tower, TowerStage, calculate_projectile_vel


class Healer(Tower):

    def __init__(self):
        super().__init__()
        self._building_cost = 35
        self._regeneration_rate = 3
        self._ability_cooldown = 1
        self._upgrade_cost = 60
        self._area_of_effect = 0
        self._detect_range = 300
        self._life_span = 10
        self._projectile_health = 30
        self._healing_rate = 10

    def _on_ability(self, *args: Enemy) -> None:
        projectile = HealerProjectile(location=self.location.copy(), velocity=(0, 0), health=self._projectile_health,
                                      healing_rate=self._healing_rate, priority=20, detect_range=self._detect_range,
                                      life_span=self._life_span)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.NONE

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._health = 400
                self._upgrade_cost = 80
                self._detect_range = 130
                self._life_span = 11
                self._projectile_health = 60
                self._healing_rate = 15
            case TowerStage.STAGE_3:
                self._health = 500
                self._detect_range = 150
                self._life_span = 12
                self._projectile_health = 100
                self._healing_rate = 25

    @property
    def max_health(self) -> int:
        return 300

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
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
        self.color = (0, 0, 0)
        self.detect_range = detect_range
        self.target = None
        self.on_target = False
        self._life_span = round(life_span * engine.window.fps)

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]):
        self._velocity = value

    def tick(self, tick_count: int) -> None:
        if self.target is None:
            towers = self.nearby_entities_type(self.detect_range, Tower)
            min_tower_health = 100000
            for tower in towers:
                if min_tower_health > tower.health > 0:
                    self.target = tower
                    min_tower_health = tower.health
        elif not self.on_target:
            self.velocity = calculate_projectile_vel(self, self.target, 5)
            self.location.add(self._velocity[0], self._velocity[1])
            collisions = self.nearby_entities_type(self._radius, Tower)
            if self.target in collisions:
                self.velocity = (0, 0)
                self.on_target = True
        if self.on_target:
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
        self.target.heal(min(self._healing_rate, self._health))
        self._health -= self._healing_rate
        if self._health <= 0:
            self.dispose()
