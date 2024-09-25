""" Python reflexion-level functionality. """
from lessmore.utils.reflexion.load_module import load_module


def get_classes(module_obj):
    module = load_module(module_obj)
    return dict([(name, cls) for name, cls in module.__dict__.items() if isinstance(cls, type)])
