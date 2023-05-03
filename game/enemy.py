import pygame.font
from pygame import Rect, Surface, Color

from engine.entity import LivingEntity
from engine.location import Location

import random

FONT = pygame.font.SysFont("comicsansms", 16, True)


class Enemy(LivingEntity):

    def __init__(self, color: Color, mouse_pos: tuple[int, int]):
        super().__init__(Location(mouse_pos[0], mouse_pos[1]), priority=10, health=200, health_bar=True)
        self.color = color
        self._type = random.randint(0, 1)
        self._target_timer = 0

    def melee_logic(self):
        pass

    def ranged_logic(self):
        pass

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

        #doing this to make an easy difference between melee and ranged enemies
        match self._type:
            case 0:
                pass
            case 1:
                pass

    def draw(self, surface: Surface) -> None:
        super().draw(surface)
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(10, 10)

    @property
    def max_health(self) -> int:
        return 200

    def _on_dispose(self) -> None:
        print(f"I am dying {self.location}")

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
