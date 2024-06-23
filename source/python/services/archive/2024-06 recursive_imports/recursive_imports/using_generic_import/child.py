from dataclasses import dataclass
import recursive_imports.using_generic_import.parent


@dataclass
class Child:
    parent: recursive_imports.using_generic_import.parent