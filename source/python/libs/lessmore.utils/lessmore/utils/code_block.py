class CodeBlock:
    def __init__(self, name, desc=""):
        self.name = name
        self.desc = desc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def code(*args, **kwargs):
    return CodeBlock(*args, **kwargs)
