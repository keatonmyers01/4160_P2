import random

from pygame import Surface, Rect

import engine
from engine.entity import Entity, LivingEntity
from engine.location import Location
from game.board import Tower, calculate_projectile_vel, Enemy, EntityTargetType, TowerStage, TowerState, TEXTURE_PATH

ARCHER_ASSETS = f'{TEXTURE_PATH}/archer'


class Archer(Tower):

    def __init__(self):
        super().__init__(scalar=3)
        self.add_state(TowerState.IDLE, ARCHER_ASSETS, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, ARCHER_ASSETS, 9)
        self._building_cost = 30
        self._max_velocity = 5
        self._dmg_amt = 20
        self._regeneration_rate = 0
        self._max_health = 200
        self._ability_cooldown = 1
        self._upgrade_cost = 30
        self._area_of_effect = 150

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = calculate_projectile_vel(self, random.choice(args), self._max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=self._dmg_amt,
                                      priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._dmg_amt = 30
                self._max_health = 300
                self._health = 300
                self._area_of_effect = 200
                self._regeneration_rate = 1
                self._upgrade_cost = 70
                self._ability_cooldown = 0.8
            case TowerStage.STAGE_3:
                self._dmg_amt = 45
                self._max_health = 450
                self._health = 450
                self._area_of_effect = 250
                self._regeneration_rate = 1
                self._ability_cooldown = 0.5

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
