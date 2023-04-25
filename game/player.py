from pygame import Rect, Surface

from engine.entity import LivingEntity


class Player(LivingEntity):

    def __init__(self):
        super().__init__()

    @property
    def max_health(self) -> int:
        pass

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass

    def draw(self, surface: Surface) -> None:
        pass

    def bounds(self) -> Rect:
        pass
