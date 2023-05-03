import random

import pygame

from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType


class Leach(Tower):

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)
        self._building_cost = 40
        self._damage = 20
        self._regeneration_rate = -1
        self._starting_health = 200
        self._max_health = 200
        self._ability_cooldown = 4
        self._health = self._starting_health
        self._upgrade_cost = 80
        self._area_of_effect = 250
        self._healing = 5
        self._aoe_radius = 80

    def _on_ability(self, *args: Enemy) -> None:
        targets = random.choice(args).nearby_entities_type(self._aoe_radius, Enemy)
        for target in targets:
            target.damage(self._damage)
            self.heal(self._healing)

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 25
                self._max_health = 250
                self._health = 250
                self._area_of_effect = 200
                self._upgrade_cost = 120
                self._healing = 7.5
            case TowerStage.STAGE_3:
                self._damage = 30
                self._max_health = 300
                self._health = 300
                self._area_of_effect = 250
                self._healing = 10

    @property
    def max_health(self) -> int:
        return 200

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
