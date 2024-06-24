from recursive_imports.using_generic_import.parent import Parent
from recursive_imports.using_generic_import.child import Child

def test():
    parent = Parent()
    child = Child(parent=parent)
    parent.child = child

    assert parent.child == child
    assert child.parent == parent

if __name__ == '__main__':
    test()