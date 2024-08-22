from inline_snapshot import snapshot
from lessmore.utils.functional.windowed import pairwise
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


def collect_indent_blocks(text: str) -> list[list[str]]:
    # - Split text into lines

    lines = ["SOF"] + ["    " + line for line in text.split("\n")] + ["EOF"]

    # - Iterate over lines

    indents_stack = [-1]  # stub value
    start_line_number_stack = [-1]  # stub value

    result = []

    for i, line in enumerate(lines):
        # - Find line indent

        if line.strip() == "":
            indent = indents_stack[-1]  # just take the last indent
        else:
            indent = len(line) - len(line.strip())

        # - Close or open the group

        # -- If the indent is less than the last indent, close the upstream groups from the stack: add to the result and pop from the stack

        if indent < indents_stack[-1]:
            while indents_stack and indent < indents_stack[-1]:
                start_line = start_line_number_stack.pop()
                result.append((start_line, i - 1))
                indents_stack.pop()

        # -- If the indent is greater than the last indent, add a new group to the stack

        if indent > indents_stack[-1]:
            indents_stack.append(indent)
            start_line_number_stack.append(i - 1)

        # -- Assert indent is equal to the last indent

        assert indent == indents_stack[-1]

    # - Return the result

    return result


def test():
    text = """\
    
    def f1():

        # - 1

        print(1)

        # - 2

        print(2)

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
    lines = text.split("\n")
    assert ["\n".join(lines[i:j]) for i, j in collect_indent_blocks(text)] == snapshot(
        [
            """\
            bar
""",
            """\
            header

            # - 4-1

            pass

            # - 4-2

            footer
""",
            """\
        # - 1
    
        print(1)

        # - 2

        print(2)

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
""",
            """\
        # - A




        # - B

""",
            """\
    def f1():

        # - 1

        print(1)

        # - 2

        print(2)

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

""",
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
