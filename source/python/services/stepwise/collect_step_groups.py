from inline_snapshot import snapshot
from lessmore.utils.functional.windowed import pairwise
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


def collect_step_groups(text: str) -> list[list[str]]:
    # - Split text into lines

    lines = ["SOF"] + ["    " + line for line in text.split("\n")] + ["EOF"]

    # - Iterate over lines

    stack = [[("start", -1, "")]]  # stub value
    indents_stack = [-1]  # # stub value
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

    # - Clean-up

    # -- Filter non-empty groups

    groups = [group for group in groups if group]

    # -- Remove the first stub group

    groups = [group for group in groups if group != [("start", -1, "")]]

    # -- Remove groups without any step

    groups = [group for group in groups if any(step[0] == "step" for step in group)]

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
    assert collect_step_groups(text) == snapshot(
        [
            [
                ("start", 25, "header"),
                ("step", 27, "# - 4-1"),
                ("step", 31, "# - 4-2"),
                ("finish", 33, "footer"),
            ],
            [
                ("start", 4, "# - 1"),
                ("step", 4, "# - 1"),
                ("step", 7, "# - 2"),
                ("step", 10, "# - 3"),
                ("step", 13, "# -- 3.1"),
                ("step", 17, "# -- 3.2"),
                ("step", 22, "# - 4"),
                ("finish", 33, "footer"),
            ],
            [("start", 37, "# - A"), ("step", 37, "# - A"), ("step", 40, "# - B"), ("finish", 40, "# - B")],
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
