""" Python reflexion-level functionality. """
import importlib
import inspect
import os.path
import sys


def load_module(module_obj, module_name=None, reload=False, import_globals=False, globals_dic=None):
    """
    :param import_globals: does not work for dependent modules properly. Use with ultimate care
    :return:
    """
    if inspect.ismodule(module_obj):
        module = module_obj
        if reload:
            module = importlib.reload(module)
    elif isinstance(module_obj, str):
        module_name = module_name or module_obj
        module = sys.modules.get(module_name)

        if not module or reload:
            if os.path.exists(module_name):
                # Consider input as path to file

                spec = importlib.util.spec_from_file_location(module_name, module_obj)
                module = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(module)
            else:

                # Consider input as module path
                module = importlib.import_module(module_name)
    else:
        raise Exception("Unknown module object")

    # put all module variables into globals to reload
    globals_dic = globals_dic or globals()
    if import_globals:
        for x in dir(module):
            if not x.startswith("_"):
                globals_dic[x] = getattr(module, x)
    return module


if __name__ == "__main__":
    print(load_module("deeplay.utils.reflexion.load_module"))
    print(load_module("deeplay.utils.reflexion.load_module", module_name="load_module"))
    print(load_module(__file__))
