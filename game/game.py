from random import randint

import pygame
from pygame.event import Event

import engine
from engine.location import Location
from engine.util import random_color
from game.enemy import Enemy
from game.grid import Grid


class Game:  # Just gonna call it "Game" for now...

    def __init__(self):
        pygame.init()
        engine.init(fps=60)
        # from here, you have access to the engine's:
        # - window
        # - event handler
        # - entity handler
        # - scheduler
        self.grid = Grid(21, 21, core_at=(10, 10))
        self.grid.location = Location.center
        engine.entity_handler.register_entity(self.grid)
        engine.event_handler.register(pygame.QUIT, self.on_quit)  # registering an event
        engine.event_handler.register(pygame.MOUSEBUTTONDOWN, self.on_left_click)
        engine.entity_handler.spawn_all()
        engine.window.start()  # starting our window - this will open it on the user's screen
        # Fair warning that this will likely crash since there are no entities being registered
        # It gives it nothing to render and eventually crashes

    def on_left_click(self, _: Event) -> None:
        random_speed = randint(1, 3)
        random_velocity = (randint(-3, 3), randint(-3, 3))
        print(random_velocity)
        print(random_speed)
        print()
        rc = random_color()
        enemy = Enemy(rc, pygame.mouse.get_pos(), random_velocity, random_speed)
        engine.entity_handler.register_entity(enemy)
        enemy.spawn()

    # example event
    # this method will be called upon a user clicking the 'X'/alt+f4/exiting the game
    def on_quit(self, _: Event) -> None:
        engine.window.stop()
