import random

import engine
from game.enemy import Enemy
from game.tower import Tower, TowerStage, EntityTargetType, TowerState, aquire_projectile_velocities, TEXTURE_PATH
from game.towers.archer import ArcherProjectile

CORE_TEXTURE_PATH = f'{TEXTURE_PATH}/core'


class CoreTower(Tower):

    def __init__(self):
        super().__init__(scalar=0.4, ticks_per_frame=4)
        self.add_state(TowerState.IDLE, CORE_TEXTURE_PATH, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, CORE_TEXTURE_PATH, 12)
        self._building_cost = 0
        self._max_velocity = 8
        self._damage = 40
        self._regeneration_rate = 1
        self._starting_health = 1000
        self._max_health = 1000
        self._ability_cooldown = 1
        self._health = self._starting_health
        self._upgrade_cost = 100
        self._area_of_effect = 150

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = aquire_projectile_velocities(self, random.choice(args), self._max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=self._damage,
                                      priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 50
                self._max_health = 1500
                self._health = 1500
                self._area_of_effect = 150
                self._regeneration_rate = 2
                self._upgrade_cost = 250
            case TowerStage.STAGE_3:
                self._damage = 80
                self._max_health = 2500
                self._health = 2500
                self._area_of_effect = 250
                self._regeneration_rate = 3

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
