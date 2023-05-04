from random import randint, choice

import pygame
from pygame import Color
from pygame.event import Event
from pygame.font import Font

import engine
from engine.entity import TiledBackground, String
from engine.location import Location
from game.board import Grid, Enemy, ON_ENEMY_DEATH
from game.constants import BG_TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, FRAMES_PER_SECOND, PIXELS_OFFSCREEN_BOUNDARY
from game.player import Player
from game.texture import Texture
from game.towers.archer import Archer
from game.towers.cannon import ShrapnelCannon
from game.towers.grapeshot import GrapeShot
from game.towers.grenadier import Grenadier
from game.towers.healer import Healer
from game.towers.leach import Leach
from game.towers.minefield import Minefield
from game.towers.sniper import Sniper

PIXEL_FONT = Font('game/asset/font/kenpixel_mini_square.ttf', 24)
TITLE_FONT = Font('game/asset/font/kenvector_future.ttf', 40)


class Game:  # Just gonna call it "Game" for now...

    def __init__(self):
        engine.init(fps=FRAMES_PER_SECOND, title='Core Defense')
        self.wave = 1
        self.bg = TiledBackground(Texture.BRICK_WALL.value, BG_TILE_SIZE)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, core_at=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.wave_str = String(TITLE_FONT, f'Wave {self.wave}', color=Color(255, 0, 255))
        self.player = Player()
        self.grid.location = Location.center
        self.wave_str.location = Location.top_center
        self.grid.cells[8][8].tower = Archer()
        self.grid.cells[5][6].tower = ShrapnelCannon()
        self.grid.cells[7][7].tower = GrapeShot()
        self.grid.cells[6][6].tower = Healer()
        self.grid.cells[5][7].tower = Leach()
        self.grid.cells[9][6].tower = Minefield()
        self.grid.cells[6][9].tower = Sniper()
        self.grid.cells[9][8].tower = Grenadier()
        engine.entity_handler.register_entities(self.grid, self.bg, self.player, self.wave_str)
        engine.entity_handler.dispose_offscreen_entities(True, pixels_offscreen=PIXELS_OFFSCREEN_BOUNDARY)
        engine.event_handler.register(pygame.QUIT, self.on_quit)  # registering an event
        engine.event_handler.register(ON_ENEMY_DEATH, self.on_enemy_death)
        self.spawn_hoarde()
        engine.entity_handler.spawn_all()
        engine.window.start()  # starting our window - this will open it on the user's screen

    def spawn_hoarde(self) -> None:
        resolution = engine.window.resolution
        for _ in range(randint(1, 25)):
            x = choice([randint(-299, 0), randint(resolution.width, resolution.width + 299)])
            y = randint(0, resolution.height)
            enemy = Enemy((x, y))
            engine.entity_handler.register_entity(enemy)
            enemy.spawn()

    def on_enemy_death(self, _: Event) -> None:
        if not len(engine.entity_handler.get_entities(Enemy)) - 1:
            self.wave += 1
            self.spawn_hoarde()
            self.wave_str.text = f'Wave {self.wave}'

    # this method will be called upon a user clicking the 'X'/alt+f4/exiting the game
    def on_quit(self, _: Event) -> None:
        engine.window.stop()
