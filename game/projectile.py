import random
import typing

from pygame import Surface, Rect

import engine
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.enemy import Enemy
from game.tower import Tower

class ArcherProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 10
        self.color = (100, 100, 100)

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
            self.on_collide(typing.cast(LivingEntity, collisions[0]))

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self, entity: LivingEntity):
        entity.damage(self._damage)
        self.dispose()


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
            self.on_collide(typing.cast(LivingEntity, collisions[0]))

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(self._radius, self._radius)

    def on_collide(self, entity: LivingEntity):
        entity.damage(self._damage)
        self.dispose()


class ShrapnelProjectileSecondary(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 4
        self.color = (175, 125, 175)

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
            self.on_collide(typing.cast(LivingEntity, collisions[0]))

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
                 velocity: tuple[int, int] = (0, 0),
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
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]):
        self._velocity = value

    def tick(self, tick_count: int) -> None:
        self.location.add(self._velocity[0], self._velocity[1])
        collisions = self.nearby_entities_type(self._radius, Enemy)
        if len(collisions) > 0:
            self.on_collide(typing.cast(LivingEntity, collisions[0]))
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
                projectile_velocity = (random.randint(-5, 5), random.randint(-5, 5))

            projectile = ShrapnelProjectileSecondary(location=self.location.copy(),
                                                     velocity=projectile_velocity,
                                                     damage=self._secondary_damage,
                                                     priority=20+i)
            engine.entity_handler.register_entity(projectile)
            projectile.spawn()
        self.dispose()


class MinefieldProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
                 damage: int = 0,
                 aoe_radius: int = 0,
                 life_span: float = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 10
        self.color = (0, 0, 0)
        self.travel_time = random.randint(15, 25)
        self._aoe_radius = aoe_radius
        self._life_span = round(life_span * engine.window.fps)

    @property
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]):
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
        for enemy in enemies:
            enemy.damage(self._damage)
        self.dispose()


class GrenadierProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
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
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]):
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

class HealerProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[int, int] = (0, 0),
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
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]):
        self._velocity = value

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


    def tick(self, tick_count: int) -> None:
        if self.target == None:
            towers = self.nearby_entities_type(self.detect_range, Tower)
            min_tower_health = 100000
            for tower in towers:
                if tower.heath < min_tower_health:
                    self.target = tower
                    min_tower_health = tower.health
        elif not self.onTarget:
            self.velocity = self.aquire_projectile_velocities(self.target, 5)
            self.location.add(self._velocity[0], self._velocity[1])
            collisions = self.nearby_entities_type(self._radius, Tower)
            if self.target in collisions:
                self.velocity = (0,0)
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
        self.target.heal(min(self._healing_rate, self._health))
        self._health -= self._healing_rate
        if self._health <= 0:
            self.dispose()