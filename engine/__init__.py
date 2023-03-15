from pygame import Color

from engine.entity import EntityHandler
from engine.window import Window, Resolution

DEF_FPS = 30
BLACK = Color(0)
DEF_NAME = 'PyGame'
DEF_RES = Resolution(1280, 720)

initialized = False
window: Window | None = None
entity_handler: EntityHandler | None = None


def init(resolution: Resolution = DEF_RES, background: Color = BLACK, title: str = DEF_NAME, fps: int = DEF_FPS):
    global initialized
    global window
    global entity_handler
    if initialized:
        raise EngineError('Cannot initialize engine more than once!')
    window = Window(resolution, background=background, title=title, fps=fps)
    entity_handler = EntityHandler()
    init.initalized = True


class EngineError(RuntimeError):

    def __init__(self, msg: str = ''):
        super().__init__(msg)
