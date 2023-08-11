from inspect import currentframe


def _get_caller_filename():
    frame = currentframe()
    frame = frame.f_back.f_back
    return frame.f_code.co_filename


def test():
    assert _get_caller_filename() == __file__


if __name__ == "__main__":
    test()
