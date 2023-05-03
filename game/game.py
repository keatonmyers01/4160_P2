import pygame
from pygame.event import Event

import engine
from engine.entity import TiledBackground
from engine.location import Location
from engine.util import random_color
from game.constants import BG_TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, FRAMES_PER_SECOND, PIXELS_OFFSCREEN_BOUNDARY
from game.enemy import Enemy
from game.grid import Grid
from game.texture import Texture


class Game:  # Just gonna call it "Game" for now...

    def __init__(self):
        engine.init(fps=FRAMES_PER_SECOND)
        self.bg = TiledBackground(Texture.BRICK_WALL, BG_TILE_SIZE)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, core_at=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.grid.location = Location.center
        engine.entity_handler.register_entity(self.grid)
        engine.entity_handler.register_entity(self.bg)
        engine.entity_handler.dispose_offscreen_entities(True, pixels_offscreen=PIXELS_OFFSCREEN_BOUNDARY)
        engine.event_handler.register(pygame.QUIT, self.on_quit)  # registering an event
        engine.event_handler.register(pygame.MOUSEBUTTONDOWN, self.on_left_click)
        engine.entity_handler.spawn_all()
        engine.window.start()  # starting our window - this will open it on the user's screen

    def on_left_click(self, event: Event) -> None:
        if event.button == pygame.BUTTON_LEFT:
            rc = random_color()
            enemy = Enemy(rc, pygame.mouse.get_pos())
            engine.entity_handler.register_entity(enemy)
            enemy.spawn()
        elif event.button == pygame.BUTTON_RIGHT:
            if entity := engine.entity_handler.get_clicked(event.pos):
                entity.dispose()

    # example event
    # this method will be called upon a user clicking the 'X'/alt+f4/exiting the game
    def on_quit(self, _: Event) -> None:
        engine.window.stop()
