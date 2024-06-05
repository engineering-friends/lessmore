from dataclasses import dataclass
from typing import Callable, Optional

from palette.teledo.element_primitives import Element


@dataclass
class CallbackInfo:
    callback: Callable
    element: Optional[Element]
