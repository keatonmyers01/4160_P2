import pygame
from pygame import Surface

import random

from engine import EngineError
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType


class Sniper(Tower):

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)
        self._building_cost = 40

        self._damage = 200
        self._regeneration_rate = 0
        self._starting_health = 250
        self._max_health = 250
        self._ability_cooldown = 3
        self._health = self._starting_health
        self._upgrade_cost = 60
        self._area_of_effect = 400

    def _on_ability(self, *args: Enemy) -> None:
        random.choice(args).damage(self._damage)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

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
                self._damage = 300
                self._max_health = 300
                self._health = 300
                self._area_of_effect = 500
                self._regeneration_rate = 0
                self._upgrade_cost = 100
            case TowerStage.STAGE_3:
                self._damage = 450
                self._max_health = 400
                self._health = 400
                self._area_of_effect = 600
                self._regeneration_rate = 0
            case _:
                raise EngineError()

    @property
    def max_health(self) -> int:
        return 250

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
