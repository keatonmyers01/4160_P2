import pygame.font
from pygame import Rect, Surface, Color

from engine.entity import Entity, String, LivingEntity
from engine.location import Location

FONT = pygame.font.SysFont("comicsansms", 16, True)


class Enemy(LivingEntity):

    def __init__(self, color: Color, mouse_pos: tuple[int, int]):
        super().__init__(Location(mouse_pos[0], mouse_pos[1]), priority=10, health=5000)
        self.color = color
        self.health_str = String(FONT, str(self._health), loc=self.location.copy())

    def _on_load(self) -> None:
        str_loc = self.bounds().midtop
        self.health_str.location = Location(str_loc[0], str_loc[1])

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)
        self.health_str.location.add(self.velocity[0], self.velocity[1])

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())
        self.health_str.draw(surface)

    def bounds(self) -> Rect:
        return self.location.as_rect(10, 10)

    def _on_dispose(self) -> None:
        print(f"I am dying {self.location}")

    def _on_damage(self) -> None:
        self.health_str.text = f'{self._health}'

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
