import pygame
from pygame import Surface

import random

import engine
from engine import EngineError
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType
from game.towers.archer import ArcherProjectile


class CoreTower(Tower):

    def __init__(self):
        super().__init__()
        self._texture = pygame.image.load(Texture.CORE_TOWER.value)
        self._texture = pygame.transform.scale(self._texture, CELL_SIZE)
        self._building_cost = 0
        self._max_velocity = 8

        self._damage = 40
        self._regeneration_rate = 1
        self._starting_health = 1000
        self._max_health = 1000
        self._ability_cooldown = 1
        self._health = self.starting_health
        self._upgrade_cost = 100
        self._area_of_effect = 150
        

    def _on_ability(self, *args: Enemy) -> None:
        projectile_velocity = self.aquire_projectile_velocities(random.choice(args), self._max_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=self._damage,
                                      priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self._texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return self._regeneration_rate

    def starting_health(self) -> int:
        return self._starting_health

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return self._building_cost

    def ability_cooldown(self) -> float:
        return self._ability_cooldown

    def area_of_effect(self) -> int:
        return self._area_of_effect

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
            case _:
                raise EngineError()

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
