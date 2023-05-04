import random

from pygame import Surface, Rect

import engine
from engine.entity import Entity
from engine.location import Location
from game.board import Tower, Enemy, calculate_projectile_vel, EntityTargetType, TowerStage, TowerState, TEXTURE_PATH

GREN_ASSETS = f'{TEXTURE_PATH}/shrap'


class Grenadier(Tower):

    def __init__(self):
        super().__init__(scalar=3)
        self.add_state(TowerState.IDLE, GREN_ASSETS, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, GREN_ASSETS, 5)
        self._building_cost = 50
        self._max_velocity = 5
        self._dmg_amt = 30
        self._regeneration_rate = 1
        self._ability_cooldown = 2
        self._upgrade_cost = 80
        self._area_of_effect = 300
        self._aoe_radius = 50

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = calculate_projectile_vel(self, random.choice(args), self._max_velocity)
        projectile = GrenadierProjectile(location=self.location.copy(), velocity=projectile_velocity,
                                         damage=self._dmg_amt, priority=20, aoe_radius=self._aoe_radius)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._dmg_amt = 40
                self._health = 400
                self._area_of_effect = 350
                self._upgrade_cost = 250
                self._aoe_radius = 60
            case TowerStage.STAGE_3:
                self._dmg_amt = 60
                self._health = 500
                self._area_of_effect = 425
                self._regeneration_rate = 2
                self._aoe_radius = 75

    @property
    def max_health(self) -> int:
        return 300

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
