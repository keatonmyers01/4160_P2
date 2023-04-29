import pygame
from pygame import Surface

from engine import EngineError
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType


class Sniper(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 150
            case TowerStage.STAGE_2:
                damage = 300
            case TowerStage.STAGE_3:
                damage = 600
            case _:
                raise EngineError('L')
        args[0].damage(damage)

    def __init__(self):
        super().__init__()
        self.texture = pygame.image.load(Texture.CORE_TOWER.value)
        self.texture = pygame.transform.scale(self.texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 0

    def starting_health(self) -> int:
        return 250

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 40

    def ability_cooldown(self) -> float:
        return 3

    def area_of_effect(self) -> int:
        return 400

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass
