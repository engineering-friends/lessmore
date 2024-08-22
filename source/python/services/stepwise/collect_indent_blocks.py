from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


def parse_indent_blocks(code: str) -> list[tuple[int, int]]:
    # - Return if text is empty

    if code.strip() == "":
        return []

    # - Split text into lines

    lines = ["SOF"] + ["    " + line for line in code.split("\n")] + ["EOF"]

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
                result.append((start_line - 1, i - 1))  # -1 because of the SOF line
                indents_stack.pop()

        # -- If the indent is greater than the last indent, add a new group to the stack

        if indent > indents_stack[-1]:
            indents_stack.append(indent)
            start_line_number_stack.append(i)

        # -- Assert indent is equal to the last indent

        assert indent == indents_stack[-1]

    # - Return the result: symbol ranges

    # -- Init ranges list

    indent_blocks = []

    # -- Calculate symbol positions for lines

    lines = code.split("\n")
    line_endings = [len(lines[0])]
    for line in lines[1:]:
        line_endings.append(line_endings[-1] + len(line) + 1)

    # -- Calculate symbol ranges

    for start_line, end_line in result:
        indent_blocks.append((line_endings[start_line - 1] + 1 if start_line != 0 else 0, line_endings[end_line - 1]))

    # -- Remove blocks with 0 length

    indent_blocks = [(start, end) for start, end in indent_blocks if start != end]

    # -- Return the result

    return indent_blocks


def test():
    code = """\
    
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

    for i, j in parse_indent_blocks(code):
        print(code[i:j])
        print("-" * 88)


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
