from pygame import Rect, Surface

from engine.color import RED, GREEN
from engine.entity import Entity, LivingEntity
from engine.location import Location


class HealthBar(Entity):

    def __init__(self, entity: LivingEntity, *, w: int = 50, h: int = 6):
        super().__init__()
        self._entity = entity
        self._w = w
        self._h = h

    def tick(self, tick_count: int) -> None:
        self.location = Location.top_and_centered(self.bounds(), self._entity.bounds())
        self.location.add(y=-5)

    def draw(self, surface: Surface) -> None:
        green_width = int((self._entity.health / self._entity.max_health) * self._w)
        surface.fill(RED, self.location.as_rect(self._w, self._h))
        surface.fill(GREEN, self.location.as_rect(green_width, self._h))

    def bounds(self) -> Rect:
        return self.location.as_rect(self._w, self._h)
