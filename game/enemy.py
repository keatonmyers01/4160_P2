import random
from enum import Enum
from threading import Timer

from pygame import Rect, Surface, Color

from engine.entity import LivingEntity
from engine.location import Location
from engine.sprite import Sprite
from game.tower import Tower, TEXTURE_PATH


class EnemyState(Enum):

    EXISTING = 'enemy'


class Enemy(Sprite):

    def __init__(self, color: Color, mouse_pos: tuple[int, int]):
        super().__init__(EnemyState.EXISTING, priority=10, health_bar=True)
        self.add_state(EnemyState.EXISTING, TEXTURE_PATH, 6)
        self.location.x = mouse_pos[0]
        self.location.y = mouse_pos[1]
        self.color = color
        self.on_cooldown = True
        self._type: bool = bool(random.randint(0, 1))
        self._target_timer: int = 0
        self.target: LivingEntity | None = None
        self._velocity: tuple[float, float] = (0, 0)
        self.max_velocity: int = 6
        self.on_target: bool = False
        self.damage: int = 25
        self.ability_cooldown: int = 0
        self._ability_timer = Timer(self.ability_cooldown, self.perform_ability)

    def calculate_travel_velocity(self) -> tuple[float, float]:
        orgin = self.location
        target_location = self.target.location
        x_distance = orgin.directional_dist_x(target_location)
        y_distance = orgin.directional_dist_y(target_location)
        total_distance = abs(y_distance) + abs(x_distance)
        distance_ratio = abs(x_distance / total_distance)
        x_velocity = distance_ratio * self.max_velocity
        y_velocity = (1 - distance_ratio) * self.max_velocity
        if x_distance < 0:
            x_velocity *= -1
        if y_distance < 0:
            y_velocity *= -1

        return x_velocity, y_velocity

    def tick(self, tick_count: int) -> None:
        super().tick(tick_count)

        # reestablish a target every second
        if self._target_timer % 30 and not self.on_target:
            target_range = 1
            targets = self.nearby_entities_type(target_range * 50, Tower)
            while len(targets) > 0:
                targets = self.nearby_entities_type(target_range * 50, Tower)
                target_range += 1
            self.target = random.choice(targets)
        self._target_timer += 1

        # move towards target
        self.location.add(self._velocity[0], self._velocity[1])

        # detect if the entity is on target
        if not self.on_target:
            self._velocity = self.calculate_travel_velocity()
            collisions = self.nearby_entities_type(10, Tower)
            if self.target in collisions:
                self._velocity = (0, 0)
                self.on_target = True

        if not self.on_cooldown:
            self.perform_ability()

    def draw(self, surface: Surface) -> None:
        super().draw(surface)
        surface.fill(self.color, self.bounds())

    def bounds(self) -> Rect:
        return self.location.as_rect(10, 10)

    def ability_cooldown(self) -> float:
        return 0.5

    def _on_ability(self):
        self.target.damage(self.damage)

    def perform_ability(self) -> None:
        if self.on_target:
            self._on_ability()
            self.on_cooldown = True
            return
        else:
            self.on_cooldown = False

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
