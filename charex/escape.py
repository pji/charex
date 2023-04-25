"""
escape
~~~~~~

Character escape schemes.
"""
from collections.abc import Callable


# Registry.
schemes: dict[str, Callable[[str, str], str]] = {}


# Registration.
class escape:
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(
        self,
        fn: Callable[[str, str], str]
    ) -> Callable[[str, str], str]:
        schemes[self.key] = fn
        return fn


# Escape schemes.
@escape('html')
def escape_html(char: str, codec: str) -> str:
    """Escape scheme for HTML entities."""
    n = ord(char)
    return f'&#{n};'


@escape('url')
def escape_url(char: str, codec: str) -> str:
    """Escape scheme for URL percent encoding."""
    b = char.encode(codec)
    octets = [f'%{x:02x}'.upper() for x in b]
    return ''.join(x for x in octets)
