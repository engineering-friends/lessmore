import re

from lessmore.utils.print_and_copy import print_and_copy
from lessmore.utils.run_inline_snapshot_tests.remove_snapshot_wrapper.find_closing_parenthesis import (
    find_closing_parenthesis,
)


def remove_snapshot_wrapper(code: str) -> str:
    # - Find all occurrences of snapshot(

    positions = [match.start() for match in re.finditer(r"snapshot\(", code)]

    # - Iterate over all occurrences of snapshot(

    for position in positions:
        # - Find closing parenthesis position

        closing_position = find_closing_parenthesis(text=code, start=position)

        if closing_position == -1:
            raise ValueError(
                f"Could not find closing parenthesis for snapshot call at position {position} in code:\n{code}"
            )

        # - Find first non-whitespace character after snapshot call

        _current_position = position + len("snapshot(")
        while code[_current_position] in [" ", "\n"]:
            _current_position += 1
        content_start_position = _current_position

        # - Extract the content inside snapshot's parentheses

        content = code[content_start_position:closing_position]

        # - Remove newline if it follows the snapshot call

        if code[closing_position] == "\n":
            code = code[:closing_position] + code[closing_position + 1 :]

        # - Replace snapshot(...) with the content

        code = code[:position] + content + code[closing_position + 1 :]

    return code


def test():
    assert remove_snapshot_wrapper("assert 1 == snapshot(1)") == "assert 1 == 1"
    assert remove_snapshot_wrapper("assert (1,2,3) == snapshot((1,2,3))") == "assert (1,2,3) == (1,2,3)"
    assert (
        remove_snapshot_wrapper(
            """assert {"a": 1, "b": 2} == snapshot(
        {
            "a": 1,
            "b": 2,
        }
    )"""
        )
        == """assert {"a": 1, "b": 2} == {
            "a": 1,
            "b": 2,
        }
    """
    )


if __name__ == "__main__":
    test()
