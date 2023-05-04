import random

from pygame import Surface, Rect

import engine
from engine.entity import Entity
from engine.location import Location
from game.board import Tower, Enemy, EntityTargetType, TowerStage


class Minefield(Tower):

    def __init__(self):
        super().__init__()
        self._building_cost = 0
        self._max_velocity = 5
        self._damage = 30
        self._regeneration_rate = 0
        self._ability_cooldown = 2
        self._upgrade_cost = 70
        self._area_of_effect = 150
        self._max_velocity = 5
        self._lifespan = 5
        self._aoe_radius = 100

    def _on_ability(self, *args: Enemy) -> None:
        velocity_seed = random.uniform(0, self._max_velocity)
        x_mod = 1
        y_mod = 1
        if random.randint(0, 1):
            x_mod *= -1
        if random.randint(0, 1):
            y_mod *= -1
        projectile_velocity = (velocity_seed * x_mod, (5 - velocity_seed) * y_mod)
        projectile = MinefieldProjectile(location=self.location.copy(), velocity=projectile_velocity,
                                         damage=self._damage, priority=20, aoe_radius=self._aoe_radius,
                                         life_span=self._lifespan)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.NONE

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 45
                self._health = 400
                self._area_of_effect = 125
                self._upgrade_cost = 100
                self._lifespan = 7
                self._aoe_radius = 110
            case TowerStage.STAGE_3:
                self._damage = 70
                self._health = 450
                self._area_of_effect = 150
                self._lifespan = 10
                self._aoe_radius = 115

    @property
    def max_health(self) -> int:
        return 300

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


class MinefieldProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0,
                 aoe_radius: int = 0,
                 life_span: float = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self.damage = damage
        self._radius = 10
        self.color = (0, 0, 0)
        self.travel_time = random.randint(15, 25)
        self._aoe_radius = aoe_radius
        self._life_span = round(life_span * engine.window.fps)

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]):
        self._velocity = value

    def tick(self, tick_count: int) -> None:
        if self.travel_time >= 0:
            self.travel_time -= 1
            self.location.add(self._velocity[0], self._velocity[1])

        if self._life_span <= 0:
            self.on_collide()
        else:
            self._life_span -= 1

        collisions = self.nearby_entities_type(self._radius, Enemy)
        if len(collisions) > 0:
            self.on_collide()

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self):
        enemies = self.nearby_entities_type(self._aoe_radius, Enemy)
        self.dispose()
