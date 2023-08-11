from lessmore.utils.modular_code.modular_class.example.modular_class import ModularClass


def test():
    modular_class = ModularClass(foo="bar")
    assert modular_class.some_method() == "bar"


if __name__ == "__main__":
    test()
