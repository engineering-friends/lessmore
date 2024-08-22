from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from more_itertools import first
from repos.lessmore.source.python.services.stepwise.collect_indent_blocks import parse_indent_blocks


def parse_ranges(code: str, offset: int = 0) -> list:
    # - Return if empty code

    if code.strip() == "":
        return []

    # - Parse indent blocks first

    indent_blocks = parse_indent_blocks(code)

    # - Iterate over indent blocks, find necessary ranges

    ranges = []

    for start, end in indent_blocks:
        # - Init block ranges

        line_ranges = []

        # - Crop code

        block_code = code[start:end]

        # - Split the lines

        lines = block_code.split("\n")

        # - Iterate over lines, add ranges to the result

        current_start = first([i for i, line in enumerate(lines) if line.strip() != ""])  # first non-empty line

        prev_step_i = None

        for i, line in enumerate(lines):
            # - Skip if empty line

            if line.strip() == "":
                continue

            # - Add range if the line starts with "# -"

            if line.strip().startswith("# -"):
                if current_start is not None:
                    line_ranges.append((current_start, i))
                current_start = None
                prev_step_i = i

            # - Update the current start

            if not line.strip().startswith("# -") and current_start is None:
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

        # - Get symbol ranges and append to the result

        _ranges = []

        # -- Calculate symbol positions for lines

        line_endings = [len(lines[0])]
        for line in lines[1:]:
            line_endings.append(line_endings[-1] + len(line) + 1)

        # -- Iterate over line blocks and calculate the start and end positions

        for i, j in line_ranges:
            start = line_endings[i + 1] - 1 if i != 0 else len(lines[0])
            end = line_endings[j - 1]

            # try to reduce the end
            while block_code[end - 1].strip() == "":
                end -= 1

            _ranges.append((start + offset, end + offset))

            # for debug
            # print("\n".join(lines[i:j]))
            # print("-" * 20)
            # print(block_code[start:end])
            # print("*" * 20)

        ranges += _ranges

    # - Return the result

    return ranges


def test():
    code = """\


# - 1

print(1)

# - 2

print(2)

# - 3


# -- 3.1

pass

# -- 3.2

pass

"""
    assert [code[i:j] for i, j in parse_ranges(code)] == snapshot(
        [
            """\
 1

print(\
""",
            """\
 2

print(\
""",
            """\
.1

pa\
""",
            """\
.2

pa\
""",
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
