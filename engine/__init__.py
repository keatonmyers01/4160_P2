from pygame import Color

from engine.entity import EntityHandler
from engine.errors import EngineError
from engine.event import EventHandler
from engine.window import Window, Resolution

DEF_FPS = 30
BLACK = Color(0)
DEF_NAME = 'PyGame'
DEF_RES = Resolution(1280, 720)

initialized = False
window: Window | None = None
event_handler: EventHandler | None = None
entity_handler: EntityHandler | None = None


def init(resolution: Resolution = DEF_RES,
         background: Color = BLACK,
         title: str = DEF_NAME,
         fps: int = DEF_FPS) -> None:
    """
    Initializes the engine and constructs basic handlers.

    :param resolution: The resolution of the window.
    :param background: The color of the background.
    :param title: The title of the window.
    :param fps: The frames per second.
    :return: None.
    """
    global initialized, window, event_handler, entity_handler
    if initialized:
        raise EngineError('Cannot initialize engine more than once!')
    window = Window(resolution, background=background, title=title, fps=fps)
    entity_handler = EntityHandler()
    event_handler = EventHandler()
    initialized = True
