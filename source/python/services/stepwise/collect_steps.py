from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


def collect_steps(text: str) -> list[list[str]]:
    # - Split text into lines

    lines = text.strip().split("\n")

    # - Iterate over lines

    stack = [[]]
    indents_stack = [0]
    groups = []

    for i, line in enumerate(lines):
        # - Skip empty lines

        if line.strip() == "":
            continue

        # - Get current value: the line number and the stripped line

        value = (line.strip(), i)

        # - Calculate the indent level

        indent = len(line) - len(line.strip())

        # - Close or open the group

        # -- If the indent is less than the last indent, close the upstream groups from the stack: add to the result and pop from the stack

        if indent < indents_stack[-1]:
            while indents_stack and indent < indents_stack[-1]:
                group = stack.pop()
                if group:
                    groups.append(group)

                indents_stack.pop()

        # -- If the indent is greater than the last indent, add a new group to the stack

        if indent > indents_stack[-1]:
            stack.append([])
            indents_stack.append(indent)

        # -- Assert indent is equal to the last indent

        assert indent == indents_stack[-1]

        # - If the indent is equal to the last indent, add the line to the last group

        if line.strip().startswith("# -"):
            stack[-1].append(value)
            continue

    # - Add the remaining groups to the result

    groups += stack

    # - Filter non-empty groups

    groups = [group for group in groups if group]

    # - Return the result

    return groups


def test():
    text = """\
    
    def foo():

        # - 1


        # - 2


        # - 3


        # -- 3.1

        pass

        # -- 3.2

        if foo:
            bar

        # - 4

        if:

            # - 4-1

            pass

            # - 4-2

            pass
    
    def foo():

        # - A


        # - B

"""
    assert collect_steps(text) == snapshot(
        [
            [("# - 4-1", 24), ("# - 4-2", 28)],
            [
                ("# - 1", 2),
                ("# - 2", 5),
                ("# - 3", 8),
                ("# -- 3.1", 11),
                ("# -- 3.2", 15),
                ("# - 4", 20),
            ],
            [("# - A", 34), ("# - B", 37)],
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests()
