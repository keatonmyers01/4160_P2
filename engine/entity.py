import uuid
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Callable, Union, Type

import pygame.image
from pygame import Surface, Rect, Color
from pygame.font import Font

import engine
from engine.color import WHITE
from engine.location import Location
from game.texture import Texture


@total_ordering
class Entity(ABC):
    """
    An abstract class that represents an entity.
    An entity is anything that can be drawn to the screen.
    """

    def __init__(self, loc: Location = Location(), priority: int = 0):
        self._id = uuid.uuid4()
        self._loc = loc
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

    def nearby_entities_type(self, radius: float, t: Type['Entity']) -> list['Entity']:
        """
        Gets a list of nearby entities within the given radius and of type t.

        :param radius: The maximum distance the entities can be, before being excluded.
        :param t: The type of the entities to look for.
        :return: A list of nearby entities within the given radius and of type t.
        """
        return [e for e in engine.entity_handler.entities if e._loc.dist(self._loc) <= radius and type(e) is t]

    def nearest_entity(self) -> 'Entity | None':
        nearest: Entity | None = None
        for entity in engine.entity_handler.entities:
            if nearest is None:
                nearest = entity
                continue
            if entity.location.dist(self.location) <= nearest.location.dist(self.location):
                nearest = entity
        return nearest

    def nearest_entity_type(self, t: Type['Entity']) -> 'Entity | None':
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


class LivingEntity(Entity):

    def __init__(self, location: Location = Location(),
                 priority: int = 0,
                 *,
                 health: int = 0,
                 velocity: tuple[int, int] = (0, 0)):
        super().__init__(location, priority)
        self._health = min(health, self.max_health)
        self._velocity = velocity

    def tick(self, tick_count: int) -> None:
        if self._health <= 0:
            self._on_death()
            self.dispose()
            return
        self.location.add(self.velocity[0], self.velocity[1])

    def damage(self, amount: int) -> None:
        self._health -= amount
        self._on_damage()

    def heal(self, amount: int) -> None:
        self._health = max(self.max_health, self._health + amount)
        self._on_heal()

    @property
    def velocity(self) -> tuple[int, int]:
        return self._velocity

    @velocity.setter
    def velocity(self, value: tuple[int, int]) -> None:
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

    def __init__(self, texture: Texture, tile_size: tuple[int, int]):
        super().__init__(priority=-1)
        self._texture = pygame.image.load(texture.value)
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
