import random

from game.board import Tower, Enemy, EntityTargetType, TowerStage


class Sniper(Tower):

    def __init__(self):
        super().__init__()
        self._building_cost = 40
        self._damage = 200
        self._regeneration_rate = 0
        self._ability_cooldown = 3
        self._upgrade_cost = 60
        self._area_of_effect = 400

    def _on_ability(self, *args: Enemy) -> None:
        random.choice(args).damage(self._damage)

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._damage = 300
                self._health = 300
                self._area_of_effect = 500
                self._regeneration_rate = 0
                self._upgrade_cost = 100
            case TowerStage.STAGE_3:
                self._damage = 450
                self._health = 400
                self._area_of_effect = 600
                self._regeneration_rate = 0

    @property
    def max_health(self) -> int:
        return 250

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
