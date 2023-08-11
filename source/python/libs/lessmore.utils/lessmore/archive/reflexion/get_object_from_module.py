""" Python reflexion-level functionality. """
from functools import reduce

from lessmore.utils.reflexion.load_module import load_module


def get_object_from_module(module_obj, object_path, default=None):
    module = load_module(module_obj)

    try:
        # iterate from module to class by class_name
        return reduce(getattr, object_path.split("."), module)
    except AttributeError:
        return default


def test():
    print(get_object_from_module(module_obj=__file__, object_path="get_object_from_module"))
    print(get_object_from_module(module_obj=__file__, object_path="foo", default="Not found"))


if __name__ == "__main__":
    test()
