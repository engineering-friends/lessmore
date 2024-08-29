
from lessmore.utils.slugify import slugify

# - Test

def test():
    assert slugify('Hello World!') == 'hello-world'

if __name__ == '__main__':
    test()
