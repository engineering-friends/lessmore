from modular_code.modular_class_by_interface.modular_class_by_interface import ModularClassInterface
from modular_code.modular_class_by_interface.moduler_class import ModularClass


class SomeMethodMixin:
    def some_method(self: ModularClassInterface) -> str:
        # <some non-trivial logic>
        return self.foo
