import pygame.font
from pygame import Rect, Surface, Color

from engine.entity import Entity, String
from engine.location import Location

FONT = pygame.font.SysFont("comicsansms", 16, True)


class Enemy(Entity):

    def __init__(self, color: Color, mouse_pos: tuple[int, int], velocity: tuple[int, int] = (0, 0), speed: int = 1, health: int = 5000):
        super().__init__(Location(mouse_pos[0], mouse_pos[1]), priority=10)
        self.color = color
        self.speed = speed
        self.health = health
        self.health_str = String(FONT, str(health), loc=self.location.copy())
        self.velocity = velocity

    def on_load(self) -> None:
        str_loc = self.bounds().midtop
        self.health_str.location = Location(str_loc[0], str_loc[1])

    def tick(self, tick_count: int) -> None:
        if tick_count % self.speed == 0:
            self.location.add(self.velocity[0], self.velocity[1])
            self.health_str.location.add(self.velocity[0], self.velocity[1])

    def draw(self, surface: Surface) -> None:
        surface.fill(self.color, self.bounds())
        self.health_str.draw(surface)

    def bounds(self) -> Rect:
        return self.location.as_rect(10, 10)
