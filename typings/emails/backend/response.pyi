"""
This type stub file was generated by pyright.
"""

class Response:
    def __init__(self, exception=..., backend=...) -> None:
        ...

    def set_exception(self, exc): # -> None:
        ...

    def raise_if_needed(self): # -> None:
        ...

    @property
    def error(self):
        ...

    @property
    def success(self): # -> bool:
        ...



class SMTPResponse(Response):
    def __init__(self, exception=..., backend=...) -> None:
        ...

    def set_status(self, command, code, text, **kwargs): # -> None:
        ...

    @property
    def success(self): # -> Literal[False] | None:
        ...

    def __repr__(self): # -> LiteralString:
        ...
