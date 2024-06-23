from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Parent:
    child: Optional['Child'] = None