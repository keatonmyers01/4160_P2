import random

from pygame import Surface, Rect

import engine
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.board import TEXTURE_PATH, Tower, TowerState, Enemy, calculate_projectile_vel, EntityTargetType, TowerStage

GRAPE_TEXTURE = f'{TEXTURE_PATH}/grape'


class GrapeShot(Tower):

    def __init__(self):
        super().__init__()
        self.add_state(TowerState.IDLE, GRAPE_TEXTURE, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, GRAPE_TEXTURE, 13)
        self._building_cost = 45
        self._max_velocity = 3
        self._damage = 25
        self._regeneration_rate = 0
        self._ability_cooldown = 1
        self._upgrade_cost = 65
        self._area_of_effect = 150
        self._projectile_count = 4

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = calculate_projectile_vel(self, random.choice(args), self._max_velocity)
        for i in range(self._projectile_count):
            dx = projectile_velocity[0] + random.uniform(-0.5, 0.5)
            dy = projectile_velocity[1] + random.uniform(-0.5, 0.5)
            projectile = GrapeShotProjectile(location=self.location.copy(), velocity=(dx, dy), damage=self._damage,
                                             priority=20 + i)
            engine.entity_handler.register_entity(projectile)
            projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 30
                self._health = 425
                self._area_of_effect = 200
                self._upgrade_cost = 90
                self._projectile_count = 6
            case TowerStage.STAGE_3:
                self._damage = 45
                self._health = 500
                self._area_of_effect = 250
                self._projectile_count = 10

    @property
    def max_health(self) -> int:
        return 350

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass


class GrapeShotProjectile(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 velocity: tuple[float, float] = (0, 0),
                 damage: int = 0):
        super().__init__(location, priority)
        self._velocity = velocity
        self._max_velocity = 5
        self._damage = damage
        self._radius = 5
        self.color = (150, 150, 150)

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
