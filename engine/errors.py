class EngineError(RuntimeError):

    def __init__(self, msg: str = ''):
        super().__init__(msg)


class BadArgument(RuntimeError):

    def __init__(self, msg: str = ''):
        super().__init__(msg)
