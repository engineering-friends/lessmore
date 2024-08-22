from inline_snapshot import snapshot
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from more_itertools import first
from repos.lessmore.source.python.services.stepwise.collect_indent_blocks import parse_indent_blocks


def parse_ranges(code: str) -> list:
    # - Return if empty code

    if code.strip() == "":
        return []

    # - Parse indent blocks first

    indent_blocks = parse_indent_blocks(code)

    # - Iterate over indent blocks, find necessary ranges

    ranges = []

    for block_start, block_end in indent_blocks:
        # - Init block ranges

        line_ranges = []

        # - Crop code

        block_code = code[block_start:block_end]

        # print("code block")
        # print(block_code)

        # - Split the lines

        lines = block_code.split("\n")

        # - Calc indent

        indent = len(lines[0]) - len(lines[0].lstrip())

        # - Iterate over lines, add ranges to the result

        current_start = first([i for i, line in enumerate(lines) if line.strip() != ""])  # first non-empty line

        prev_step_i = None

        for i, line in enumerate(lines):
            # - Skip if empty line

            if line.strip() == "":
                continue

            # - Add range if the line starts with "# -"

            if line[indent:].startswith("# -"):
                if current_start is not None:
                    line_ranges.append((current_start, i))
                current_start = None
                prev_step_i = i

            # - Update the current start

            if not line[indent:].startswith("# -") and current_start is None:
                current_start = prev_step_i

        # - Add the last one

        if current_start is not None:
            line_ranges.append(
                (
                    current_start,
                    first([i for i, line in enumerate(lines) if line.strip() != ""][::-1]) + 1,  # last non-empty line
                )
            )

        # - Remove the first one if it's all empty lines

        if "\n".join(lines[line_ranges[0][0] : line_ranges[0][1]]).strip() == "":
            line_ranges.pop(0)

        # - Remove if there is only one block (meaning no step found)

        if len(line_ranges) == 1:
            continue

        # - Get symbol ranges and append to the result

        _ranges = []

        # -- Calculate symbol positions for lines

        line_endings = [len(lines[0])]
        for line in lines[1:]:
            line_endings.append(line_endings[-1] + len(line) + 1)

        # -- Iterate over line blocks and calculate the start and end positions

        for i, j in line_ranges:
            start = line_endings[i + 1] - 1 if lines[i][indent:].startswith("# -") else 0
            end = line_endings[j - 1]

            # try to reduce the end
            while block_code[end - 1].strip() == "":
                end -= 1

            _ranges.append((start + block_start, end + block_start))

            # for debug
            # print("\n".join(lines[i:j]))
            # print("-" * 20)
            # print(block_code[start:end])
            # print("*" * 20)

        ranges += _ranges

    # - Return the result

    return [(i, j) for i, j in ranges if i != j]


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

    # for value in ["\n".join(code.split("\n")[i:j]) for i, j in parse_ranges(code)]:
    #     print("-" * 88)
    #     print(value)
    #     print("*" * 88)

    for i, j in parse_ranges(code):
        print("-" * 88)
        print(i, j)
        print(code[i:j])
        print("*" * 88)

    assert [code[i:j] for i, j in parse_ranges(code)] == snapshot(
        [
            "            header",
            """\


            pass\
""",
            """\


            footer\
""",
            """\


        print(1)\
""",
            """\


        print(2)\
""",
            """\


        pass\
""",
            """\


        if f1_1:
            bar\
""",
            """\


        if:
            header

            # - 4-1

            pass

            # - 4-2

            footer\
""",
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
