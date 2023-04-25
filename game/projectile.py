import random
import typing

from pygame import Surface, Rect

import engine
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.enemy import Enemy

# class ArcherProjectile(Entity):
#
#     def __init__(self, location: Location = Location(),
#                  priority: int = 0,
#                  *,
#                  velocity: tuple[int, int] = (0, 0),
#                  target: Type[Entity],
#                  follow: bool = False,
#                  max_velocity: int = 0):
#         super().__init__(location, priority)
#         self._velocity = velocity
#         self._target = target
#         self._follow = follow
#         self._max_velocity = max_velocity
#
#     @property
#     def velocity(self) -> tuple[int, int]:
#         return self._velocity
#
#     @velocity.setter
#     def velocity(self, value: tuple[int, int]):
#         self._velocity = value
#
#     def tick(self, tick_count: int) -> None:
#         if self._target.removed:
#             self.dispose()
#             return
#         if self._target.collides_with(self):
#             self.on_collide()
#             return
#         if self._follow:
#             target_location = self._target.location
#             x_distance = self.location.dist_x(target_location)
#             y_distance = self.location.dist_y(target_location)
#             total_distance = abs(y_distance) + abs(x_distance)
#             distance_ratio = abs(x_distance / total_distance)
#             x_velocity = round(distance_ratio * self._max_velocity)
#             y_velocity = round((1 - distance_ratio) * self._max_velocity)
#             if x_distance < 0:
#                 x_velocity *= -1
#             if y_distance < 0:
#                 y_velocity *= -1
#
#             self.velocity = (x_velocity, y_velocity)
#
#     @abstractmethod
#     def on_collide(self):
#         pass


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
