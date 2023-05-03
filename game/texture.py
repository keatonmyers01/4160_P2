from enum import Enum


class Texture(Enum):
    # Basically, we'll just store the path of the texture (relative to game.py)
    # Optionally, if we wanted to segregate our textures by type (tower, environment, etc.)
    # we can create an enum for each type
    CELL = 'game/asset/envrnmt/cell.png'
    BRICK_WALL = 'game/asset/envrnmt/brick.png'
