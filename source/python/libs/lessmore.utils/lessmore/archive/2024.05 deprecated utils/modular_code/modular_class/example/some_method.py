from lessmore.utils.modular_code.modular_class.example.modular_class_data import ModularClassData


def some_method(self: ModularClassData):
    # <some non-trivial logic>
    return self.foo


def test():
    assert some_method(ModularClassData(foo="bar")) == "bar"


if __name__ == "__main__":
    test()
