from random import randint

from pygame import Color


def random_color() -> Color:
    return Color(randint(0, 255), randint(0, 255), randint(0, 255))


def min_max(value: int, min_v: int, max_v: int) -> int:
    if value < min_v:
        return min_v
    if value > max_v:
        return max_v
    return value
