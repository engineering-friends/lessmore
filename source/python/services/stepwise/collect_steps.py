from inline_snapshot import snapshot
from lessmore.utils.functional.windowed import pairwise
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


def collect_steps(text: str) -> list[list[str]]:
    # - Split text into lines

    lines = ["SOF"] + text.strip().split("\n") + ["EOF"]

    # - Iterate over lines

    stack = [[("start", -1, "")]]
    indents_stack = [-1]
    groups = []

    prev_i = -1
    prev_line = ""

    for i, line in enumerate(lines):
        # - Skip empty lines

        if line.strip() == "":
            continue

        # - Calculate the indent level

        indent = len(line) - len(line.strip())

        # - Close or open the group

        # -- If the indent is less than the last indent, close the upstream groups from the stack: add to the result and pop from the stack

        if indent < indents_stack[-1]:
            while indents_stack and indent < indents_stack[-1]:
                group = stack.pop()
                group.append(("finish", prev_i, prev_line.strip()))
                groups.append(group)
                indents_stack.pop()

        # -- If the indent is greater than the last indent, add a new group to the stack

        if indent > indents_stack[-1]:
            stack.append([("start", i, line.strip())])
            indents_stack.append(indent)

        # -- Assert indent is equal to the last indent

        assert indent == indents_stack[-1]

        # - If the indent is equal to the last indent, add the line to the last group

        if line.strip().startswith("# -"):
            stack[-1].append(("step", i, line.strip()))

        # - Update the previous line

        prev_i = i
        prev_line = line

    # - Add the remaining groups to the result

    groups += stack

    # - Filter non-empty groups

    groups = [group for group in groups if group]

    # - Remove the first stub group

    groups = [group for group in groups if group != [("start", -1, "")]]

    # - Return the result

    return groups


def test():
    text = """\
    
    def f1():

        # - 1


        # - 2


        # - 3


        # -- 3.1

        pass

        # -- 3.2

        if f1_1:
            bar

        # - 4

        if:
            header

            # - 4-1

            pass

            # - 4-2

            footer

    def f2():

        # - A


        # - B

"""
    assert collect_steps(text) == snapshot(
        [
            [("start", 19, "bar"), ("finish", 19, "bar")],
            [("start", 24, "header"), ("step", 26, "# - 4-1"), ("step", 30, "# - 4-2"), ("finish", 32, "footer")],
            [
                ("start", 3, "# - 1"),
                ("step", 3, "# - 1"),
                ("step", 6, "# - 2"),
                ("step", 9, "# - 3"),
                ("step", 12, "# -- 3.1"),
                ("step", 16, "# -- 3.2"),
                ("step", 21, "# - 4"),
                ("finish", 32, "footer"),
            ],
            [("start", 36, "# - A"), ("step", 36, "# - A"), ("step", 39, "# - B"), ("finish", 39, "# - B")],
            [("start", 34, "def f2():"), ("finish", 39, "# - B")],
            [("start", 0, "SOF")],
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
