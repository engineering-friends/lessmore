from typing import *

from more_itertools import repeatfunc as _repeatfunc, take as head

from lessmore.utils.functional.repeat_func.kwargs_to_args import kwargs_to_args


# todo later: better naming? [@marklidenberg]


def repeat_func(func: Callable, times: Optional[int], kwargs: Any) -> Iterable:
    return _repeatfunc(
        func,
        times,
        *kwargs_to_args(func, kwargs),
    )


def test():
    print(
        head(
            3,
            repeat_func(
                func=lambda x: x + 1,
                times=None,
                kwargs={"x": 1},
            ),
        )
    )


if __name__ == "__main__":
    test()
