import random

from pygame import Surface, Rect

import engine
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.enemy import Enemy
from game.tower import Tower, TowerStage, EntityTargetType, calculate_projectile_vel


class ShrapnelCannon(Tower):

    def __init__(self):
        super().__init__()
        self._building_cost = 40
        self._max_velocity = 3
        self._damage = 15
        self._regeneration_rate = 0
        self._max_health = 350
        self._ability_cooldown = 2
        self._upgrade_cost = 50
        self._area_of_effect = 250
        self._secondary_count = 6

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = calculate_projectile_vel(self, random.choice(args), self._max_velocity)
        projectile = ShrapnelProjectile(location=self.location.copy(), velocity=projectile_velocity,
                                        damage=self._damage, priority=20, secondary_count=self._secondary_count)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 30
                self._max_health = 450
                self._health = 450
                self._area_of_effect = 300
                self._regeneration_rate = 0
                self._upgrade_cost = 250
                self._secondary_count = 12
            case TowerStage.STAGE_3:
                self._damage = 30
                self._max_health = 650
                self._health = 650
                self._area_of_effect = 400
                self._regeneration_rate = 1
                self._secondary_count = 20

    @property
    def max_health(self) -> int:
        return 350

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
        self.color = (0, 0, 0)

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
            x_velocity = 0
            y_velocity = 0
            while abs(x_velocity) + abs(y_velocity) < 5:
                x_velocity = random.uniform(0, 5)
                y_velocity = random.uniform(0, 5)
                if random.randint(0, 1):
                    x_velocity *= -1
                if random.randint(0, 1):
                    y_velocity *= -1

            projectile_velocity = (x_velocity, y_velocity)

            projectile = ShrapnelProjectileSecondary(location=self.location.copy(),
                                                     velocity=projectile_velocity,
                                                     damage=self._secondary_damage,
                                                     priority=20 + i)
            engine.entity_handler.register_entity(projectile)
            projectile.spawn()
        self.dispose()
