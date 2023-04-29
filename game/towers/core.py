import pygame
from pygame import Surface

import engine
from engine import EngineError
from game.constants import CELL_SIZE
from game.enemy import Enemy
from game.texture import Texture
from game.tower import Tower, TowerStage, EntityTargetType
from game.towers.archer import ArcherProjectile


class CoreTower(Tower):

    def _on_ability(self, *args: Enemy) -> None:
        match self.stage:
            case TowerStage.STAGE_1:
                damage = 40
                max_velocity = 8
            case TowerStage.STAGE_2:
                damage = 50
                max_velocity = 8
            case TowerStage.STAGE_3:
                damage = 80
                max_velocity = 8
            case _:
                raise EngineError()

        projectile_velocity = self.aquire_projectile_velocities(args[0], max_velocity)
        print(projectile_velocity)
        projectile = ArcherProjectile(location=self.location.copy(), velocity=projectile_velocity, damage=damage,
                                      priority=20)
        engine.entity_handler.register_entity(projectile)
        projectile.spawn()

    def __init__(self):
        super().__init__()
        self._texture = pygame.image.load(Texture.CORE_TOWER.value)
        self._texture = pygame.transform.scale(self._texture, CELL_SIZE)

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

    def draw(self, surface: Surface) -> None:
        surface.blit(self._texture, self.location.as_tuple())

    def regeneration_rate(self) -> int:
        return 1

    def starting_health(self) -> int:
        return 500

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def build_cost(self) -> int:
        return 0

    def ability_cooldown(self) -> float:
        return 1

    def area_of_effect(self) -> int:
        return 100

    def _on_upgrade(self, stage: TowerStage) -> None:
        pass

    @property
    def max_health(self) -> int:
        return 1000

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
