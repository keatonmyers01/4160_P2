import uuid
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Callable, Union, Type, TypeVar

import pygame.image
from pygame import Surface, Rect, Color
from pygame.font import Font

import engine
from engine.color import WHITE, RED, GREEN, BLACK
from engine.location import Location
from engine.util import min_max

T = TypeVar('T', bound='Entity')


@total_ordering
class Entity(ABC):
    """
    An abstract class that represents an entity.
    An entity is anything that can be drawn to the screen.
    """

    def __init__(self, loc: Location | None = None, priority: int = 0):
        self._id = uuid.uuid4()
        self._loc = loc if loc else Location(0, 0)
        self._dirty = True
        self._loaded = False
        self._visible = False
        self._removed = False
        self._should_remove = False
        self._priority = priority

    # Methods used to implement class comparison (used for sorting based on priority)

    def __lt__(self, other: 'Entity') -> bool:
        return self._priority < other._priority

    def __eq__(self, other: 'Entity') -> bool:
        return self._id == other._id

    def __gt__(self, other: 'Entity'):
        return self._priority > other._priority

    # Abstract methods

    @abstractmethod
    def tick(self, tick_count: int) -> None:
        """
        Ticks the Entity, telling it to update its internal state before the next draw call.

        :param tick_count: The current tick, represented by an int, where 0 <= tick_count < FPS.
        :return: None
        """
        pass

    @abstractmethod
    def draw(self, surface: Surface) -> None:
        """
        Tells the Entity to draw itself to the given Surface.

        :param surface: The surface to draw to.
        :return: None
        """
        pass

    @abstractmethod
    def bounds(self) -> Rect:
        """
        Gets the bounding box of the Entity.
        Used for collision detection.

        :return: The bounding box of the Entity
        """
        pass

    # Optional method

    def _on_load(self) -> None:
        """
        Used to load anything the Entity hasn't already loaded upon instantiation.

        Optional method.

        :return: None
        """
        pass

    def _on_dispose(self) -> None:
        """
        Used to unload anything the Entity hasn't already on disposal of the Entity.

        Optional method.

        :return: None
        """
        pass

    # Properties

    @property
    def location(self) -> Location:
        """
        Gets the current location of the Entity.

        :return: The x and y coordinates of the Entity.
        """
        return self._loc

    @location.setter
    def location(self, value: Union[Location, Callable[[Rect], Location]]) -> None:
        """
        Sets the location of the Entity.

        Can either pass a new Location instance or a `def foo(Rect) -> Location` method.

        :param value: The new location or a method to fetch the location.
        :return: None
        """
        self._loc = value if isinstance(value, Location) else value(self.bounds())

    @property
    def priority(self) -> int:
        """
        Gets the render priority of the Entity.

        The higher the priority, the later it will be rendered, making it look like it's on top of other entities.
        The lower the priority, the sooner it will be rendered, making it look like it's under other entities.

        :return: The render priority, as an int.
        """
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:
        """
        Sets the render priority of the Entity and marks the current Entity instance as `dirty`.

        The higher the priority, the later it will be rendered, making it look like it's on top of other entities.
        The lower the priority, the sooner it will be rendered, making it look like it's under other entities.

        :param value: The new render priority.
        :return: None
        """
        self._priority = value
        self._dirty = True

    @property
    def visible(self) -> bool:
        """
        Checks whether the Entity is visible.

        If `False`, the current instance will return `False` for `should_render() -> bool`.

        :return: True if the Entity is visible, False otherwise.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """
        Sets whether the Entity is visible.

        If `False`, the current instance will return `False` for `should_render() -> bool`.

        :param value: True to set the Entity as visible, False otherwise.
        :return: None
        """
        self._visible = value

    @property
    def dirty(self) -> bool:
        """
        Checks if the Entity's state has been updated since last tick and needs to be updated in the Entity Handler.

        Calling `clean()` will reset this back to the default, False.

        :return: True if the Entity's state has been updated since last tick, False otherwise.
        """
        return self._dirty

    @property
    def removed(self) -> bool:
        """
        Checks if the Entity has been removed.

        :return: True if the Entity has been removed, False otherwise.
        """
        return self._removed

    # Methods

    def should_draw(self) -> bool:
        """
        Checks if the Entity should be drawn to the Surface.

        :return: True if the Entity should be drawn to the Window, False otherwise.
        """
        return self._visible and self._loaded and not self._removed

    def should_remove(self) -> bool:
        """
        Checks if the Entity should be removed by the EntityHandler.

        :return: True if the Entity should be removed by the Window, False otherwise.
        """
        if not self._loaded:
            return False
        return self._should_remove and not self._removed

    def dispose(self) -> None:
        """
        Marks the given Entity as disposable.
        This will tell the EntityHandler that it should remove this Entity.

        :return: None.
        """
        self._should_remove = True
        self._on_dispose()

    def spawn(self) -> None:
        """
        Spawns the Entity.
        Calls on_load() and sets the entity's visibility to True.

        :return: None.
        """
        if not self._loaded:
            self._on_load()
            self._loaded = True
            self._visible = True

    def clean(self) -> None:
        """
        Tells the Entity that its state has been updated by the Entity Handler.

        :return: None
        """
        self._dirty = False

    def clicked_on(self, mouse_pos: tuple[int, int]) -> bool:
        """
        Checks if the Entity was clicked on, given the mouse position.

        :param mouse_pos: The coordinates of the mouse as a tuple (x, y)
        :return: True if the Entity collides with the given mouse position, false otherwise.
        """
        return self.bounds().collidepoint(mouse_pos)

    def collides_with(self, entity: 'Entity') -> bool:
        """
        Checks if the given Entity is colliding with the current Entity instance.

        :param entity: The other entity to check.
        :return: True if the Entity collides with the current instance, false otherwise.
        """
        return self.bounds().colliderect(entity.bounds())

    def nearby_entities(self, radius: float) -> list['Entity']:
        """
        Gets a list of nearby entities within the given radius.

        :param radius: The maximum distance the entities can be, before being excluded.
        :return: A list of nearby entities within the given radius.
        """
        return [e for e in engine.entity_handler.entities if e.location.dist(self.location) <= radius]

    def nearby_entities_type(self, radius: float, t: Type[T]) -> list[T]:
        """
        Gets a list of nearby entities within the given radius and of type t.

        :param radius: The maximum distance the entities can be, before being excluded.
        :param t: The type of the entities to look for.
        :return: A list of nearby entities within the given radius and of type t.
        """
        return [e for e in engine.entity_handler.entities if e._loc.dist(self._loc) <= radius and isinstance(e, t)]

    def nearest_entity(self) -> 'Entity | None':
        nearest: Entity | None = None
        for entity in engine.entity_handler.entities:
            if nearest is None:
                nearest = entity
                continue
            if entity.location.dist(self.location) <= nearest.location.dist(self.location):
                nearest = entity
        return nearest

    def nearest_entity_type(self, t: Type[T]) -> 'T | None':
        nearest: Entity | None = None
        for entity in engine.entity_handler.entities:
            if not isinstance(entity, t):
                continue
            if nearest is None:
                nearest = entity
                continue
            if entity.location.dist(self.location) <= nearest.location.dist(self.location):
                nearest = entity
        return nearest


class HealthBar(Entity):

    def __init__(self, entity: 'LivingEntity', *, w: int = 50, h: int = 6):
        super().__init__()
        self._entity = entity
        self._w = w
        self._h = h

    def tick(self, tick_count: int) -> None:
        self.location = Location.top_and_centered(self.bounds(), self._entity.bounds())
        self.location.sub(y=5)

    def draw(self, surface: Surface) -> None:
        green_width = int((self._entity.health / self._entity.max_health) * self._w)
        surface.fill(RED, self.location.as_rect(self._w, self._h))
        surface.fill(GREEN, self.location.as_rect(green_width, self._h))

    def bounds(self) -> Rect:
        return self.location.as_rect(self._w, self._h)


class LivingEntity(Entity):

    def __init__(self,
                 priority: int = 0,
                 *,
                 health: int = 10,
                 velocity: tuple[float, float] = (0, 0),
                 health_bar: bool = False,
                 bound_to_screen: bool = False):
        super().__init__(priority=priority)
        self._health = max(health, self.max_health)
        self._max_health = self.max_health
        self._velocity = velocity
        self._health_bar: HealthBar | None = HealthBar(self) if health_bar else None
        self._bound_to_screen = bound_to_screen
        self._invincible = False
        self._invincible_frames = 0

    def tick(self, tick_count: int) -> None:
        if self._health_bar:
            self._health_bar.tick(tick_count)
        if self._health <= 0:
            self._on_death()
            self.dispose()
            return
        if self._invincible_frames > 0:
            self._invincible_frames -= 1
        if not self._bound_to_screen:
            self.location.add(self.velocity[0], self.velocity[1])
        else:
            new_x = self.location.x + self.velocity[0]
            new_y = self.location.y + self.velocity[1]
            bounds = self.bounds()
            resolution = engine.window.resolution
            new_x = min_max(int(new_x), 0, resolution.width - bounds.width)
            new_y = min_max(int(new_y), 0, resolution.height - bounds.height)
            self.location.x = new_x
            self.location.y = new_y

    def draw(self, surface: Surface) -> None:
        if self._health_bar:
            self._health_bar.draw(surface)

    def spawn(self) -> None:
        super().spawn()
        if self._health_bar:
            self._health_bar.spawn()

    def dispose(self) -> None:
        super().dispose()
        if self._health_bar:
            self._health_bar.dispose()

    def damage(self, amount: int) -> None:
        if self._invincible or self._invincible_frames > 0:
            return
        self._health -= amount
        self._on_damage()

    def heal(self, amount: int) -> None:
        self._health = min(self._max_health, (self._health + amount))
        self._on_heal()

    @property
    def is_moving(self) -> bool:
        return self._velocity[0] != 0 or self._velocity[1] != 0

    @property
    def velocity(self) -> tuple[float, float]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[float, float]) -> None:
        self._velocity = value

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        if value <= 0:
            self._health = 0
            self._on_death()

    @property
    def invincible(self) -> bool:
        return self._invincible

    @invincible.setter
    def invincible(self, value: bool) -> None:
        self._invincible = value

    @property
    def invincible_frames(self) -> int:
        return self._invincible_frames

    @invincible_frames.setter
    def invincible_frames(self, value: int) -> None:
        self._invincible_frames = max(0, value)

    @property
    @abstractmethod
    def max_health(self) -> int:
        pass

    @abstractmethod
    def _on_damage(self) -> None:
        pass

    @abstractmethod
    def _on_heal(self) -> None:
        pass

    @abstractmethod
    def _on_death(self) -> None:
        pass


class EntityHandler:
    """
    Represents an Entity repository. Handles passive Entity updating and drawing.
    """

    def __init__(self):
        self._entities: list[Entity] = []
        self._despawn_offscreen = False
        self._safe_rect: Rect | None = None

    def tick(self, tick_count: int) -> None:
        """
        Ticks all registered entities.
        Also checks:
        - If any entity's render priorities have changed, if true, will be re-sorted.
        - If any entity is marked as disposed, if true, will remove the entity.

        :param tick_count: The current tick count.
        :return: None.
        """
        if self._check_dirty():
            self._entities.sort()

        for entity in self._entities:
            if self._despawn_offscreen:
                if not self._safe_rect.colliderect(entity.bounds()):
                    entity.dispose()
            if entity.should_remove():
                self._entities.remove(entity)
                del entity
                continue
            entity.tick(tick_count)

    def draw(self, surface: Surface) -> None:
        """
        Draws all registered entities.
        If the entity is invisible or should not be drawn, it will be skipped over.

        :param surface: The surface to draw to.
        :return: None.
        """
        for entity in self._entities:
            if entity.should_draw():
                entity.draw(surface)

    def register_entities(self, *args: Entity) -> None:
        """
        Registers the given entities, sorted by their render priority.

        :param args: The entities to register.
        :return: None.
        """
        self._entities.extend(args)

    def register_entity(self, entity: Entity) -> None:
        """
        Registers the given entity, sorted by their render priority.

        :param entity: The entity to register.
        :return: None.
        """
        self._entities.append(entity)

    def spawn_all(self) -> None:
        """
        Spawns all registered entities, regardless if they're already spawned.

        :return: None.
        """
        for entity in self._entities:
            entity.spawn()

    def dispose_all(self) -> None:
        """
        Disposes all registered entities, regardless if they're already marked for disposal.

        On the next tick, all registered entities will be removed.

        :return: None.
        """
        for entity in self._entities:
            entity.dispose()

    def clear(self) -> None:
        """
        Clears all entities. Does not call `Entity.dispose()`.

        :return: None.
        """
        self.dispose_all()
        self._entities.clear()

    def get_clicked(self, mouse_pos: tuple[int, int]) -> Entity | None:
        """
        Gets the first Entity that's bounding box collides with the given mouse_pos.
        Entities are sorted by render priority, from highest to lowest.
        If no Entity collides with the given mouse_pos, None is returned.

        :param mouse_pos: The coordinates of the mouse, on click.
        :return: An optional Entity that's bounding box collides with the given mouse_pos.
        """
        for entity in reversed(self._entities):
            if entity.visible and entity.clicked_on(mouse_pos):
                return entity
        return None

    @property
    def entities(self) -> list[Entity]:
        """
        Gets a list of Entity's, sorted by their render priority.

        :return: A list of entities, sorted by their render priority.
        """
        return self._entities

    def get_entities(self, entity_type: Type[Entity]) -> list[Entity]:
        """
        Gets a list of Entity's that are of type `entity_type`.

        :param entity_type: The type of Entity to look for.
        :return: A list of Entity's that are of type `entity_type`.
        """
        return [e for e in self._entities if isinstance(e, entity_type)]

    def dispose_offscreen_entities(self, dispose: bool, *, pixels_offscreen: int = 0) -> None:
        """
        Tells the Entity Handler to dispose entities that are off the screen by the given
        `pixels_offscreen` radius. Takes into account the window's width and height.

        :param dispose: Whether to dispose of the offscreen entities.
        :param pixels_offscreen: The distance away from the screen to dispose.
        :return: None
        """
        resolution = engine.window.resolution
        self._despawn_offscreen = dispose
        self._safe_rect = Rect(-pixels_offscreen,
                               -pixels_offscreen,
                               resolution.width + (pixels_offscreen * 2),
                               resolution.height + (pixels_offscreen * 2))

    def _check_dirty(self) -> bool:
        """
        Checks if any of the registered entities have been changed since last tick.

        :return: True if a registered entity has been changed since last tick, false otherwise.
        """
        for entity in self._entities:
            if entity.dirty:
                return True
        return False


class String(Entity):

    def __init__(self, font: Font, text: str, *, color: Color = WHITE, loc: Location = Location(0, 0)):
        super().__init__(loc, priority=2)
        self._font = font
        self._color = color
        self._text = text
        self._surface = self._font.render(text, True, self._color)
        self._surface.get_rect().x = self._loc.x
        self._surface.get_rect().y = self._loc.y

    def tick(self, tick_count: int) -> None:
        # Do nothing
        pass

    def draw(self, surface: Surface) -> None:
        surface.blit(self._surface, self._loc.as_tuple())

    def bounds(self) -> Rect:
        return self._surface.get_rect()

    def _rerender(self) -> None:
        self._surface = self._font.render(self._text, True, self._color)
        self._surface.get_rect().x = self._loc.x
        self._surface.get_rect().y = self._loc.y

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
        self._rerender()

    @Entity.location.setter
    def location(self, value: Union[Location, Callable[[Rect], Location]]) -> None:
        self._loc = value if isinstance(value, Location) else value(self.bounds())
        self._rerender()

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        self._color = value
        self._rerender()


class TiledBackground(Entity):

    def __init__(self, texture: str, tile_size: tuple[int, int]):
        super().__init__(priority=-1)
        self._texture = pygame.image.load(texture)
        self._texture = pygame.transform.scale(self._texture, tile_size)

    def tick(self, tick_count: int) -> None:
        # do nothing
        pass

    def draw(self, surface: Surface) -> None:
        res = engine.window.resolution
        for x in range(0, res.width, self._texture.get_width()):
            for y in range(0, res.height, self._texture.get_height()):
                surface.blit(self._texture, (x, y))

    def bounds(self) -> Rect:
        res = engine.window.resolution
        return self.location.as_rect(res.width, res.height)


class StrokedString(Entity):

    def __init__(self, font: Font, text: str, fg: Color = WHITE, bg: Color = BLACK):
        super().__init__()
        self._font = font
        self._text = text
        self._fg = fg
        self._bg = bg
        self._rerender()

    def tick(self, tick_count: int) -> None:
        # do nothing
        pass

    def draw(self, surface: Surface) -> None:
        surface.blit(self._surface, self.location.as_tuple())

    def bounds(self) -> Rect:
        return self._surface.get_rect()

    def _rerender(self) -> None:
        self._surface = self._font.render(self._text, True, self._fg)
        self._surface = self._outline(self._surface, 10, self._bg)

    def _outline(self, image: Surface, thickness: int, color: Color, color_key: tuple = (255, 0, 255)) -> Surface:
        mask = pygame.mask.from_surface(image)
        mask_surf = mask.to_surface(setcolor=color)
        mask_surf.set_colorkey((0, 0, 0))

        new_img = pygame.Surface((image.get_width() + 2, image.get_height() + 2))
        new_img.fill(color_key)
        new_img.set_colorkey(color_key)

        for i in -thickness, thickness:
            new_img.blit(mask_surf, (i + thickness, thickness))
            new_img.blit(mask_surf, (thickness, i + thickness))
        new_img.blit(image, (thickness, thickness))

        return new_img

    def _circle_points(self, r: int) -> list[tuple[int, int]]:
        x, y, e = r, 0, 1 - r
        points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
        self._rerender()

    @Entity.location.setter
    def location(self, value: Union[Location, Callable[[Rect], Location]]) -> None:
        self._loc = value if isinstance(value, Location) else value(self.bounds())
        self._rerender()

    @property
    def fg(self) -> Color:
        return self._fg

    @fg.setter
    def fg(self, value: Color) -> None:
        self._fg = value
        self._rerender()

    @property
    def bg(self) -> Color:
        return self._bg

    @bg.setter
    def bg(self, value: Color) -> None:
        self._bg = value
        self._rerender()
