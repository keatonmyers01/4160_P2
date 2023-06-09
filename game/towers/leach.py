import random

from game.board import Tower, Enemy, EntityTargetType, TowerStage, TowerState
from game.constants import TEXTURE_PATH

LEACH_ASSET = f'{TEXTURE_PATH}/tower/leach'


class Leach(Tower):

    def __init__(self):
        super().__init__(scalar=3, ticks_per_frame=4)
        self.add_state(TowerState.IDLE, LEACH_ASSET, 1)
        self.add_state(TowerState.PERFORMING_ABILITY, LEACH_ASSET, 11)
        self._building_cost = 40
        self._dmg_amt = 20
        self._regeneration_rate = -1
        self._ability_cooldown = 4
        self._upgrade_cost = 80
        self._area_of_effect = 250
        self._healing = 5
        self._aoe_radius = 80

    def _on_ability(self, *args: Enemy) -> None:
        targets = random.choice(args).nearby_entities_type(self._aoe_radius, Enemy)
        for target in targets:
            target.damage(self._dmg_amt)
            self.heal(self._healing)

    def entity_target(self) -> EntityTargetType:
        return EntityTargetType.ENEMY

    def _on_upgrade(self, stage: TowerStage) -> None:
        match stage:
            case TowerStage.STAGE_2:
                self._dmg_amt = 25
                self._health = 250
                self._area_of_effect = 200
                self._upgrade_cost = 120
                self._healing = 7.5
            case TowerStage.STAGE_3:
                self._dmg_amt = 30
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
