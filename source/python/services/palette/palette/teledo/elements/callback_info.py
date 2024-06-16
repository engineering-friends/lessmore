from dataclasses import dataclass
from typing import Callable, Optional

from palette.teledo.elements.element import Element


@dataclass
class CallbackInfo:
    callback: Callable
    element: Optional[Element]
