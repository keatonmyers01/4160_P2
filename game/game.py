import pygame
from pygame.event import Event

import engine


class Game:  # Just gonna call it "Game" for now...

    def __init__(self):
        pygame.init()
        engine.init()
        # from here, you have access to the engine's:
        # - window
        # - event handler
        # - entity handler
        # - scheduler
        engine.event_handler.register(pygame.QUIT, self.on_quit)  # registering an event
        engine.window.start()  # starting our window - this will open it on the user's screen
        # Fair warning that this will likely crash since there are no entities being registered
        # It gives it nothing to render and eventually crashes

    # example event
    # this method will be called upon a user clicking the 'X'/alt+f4/exiting the game
    def on_quit(self, _: Event) -> None:
        engine.window.stop()
