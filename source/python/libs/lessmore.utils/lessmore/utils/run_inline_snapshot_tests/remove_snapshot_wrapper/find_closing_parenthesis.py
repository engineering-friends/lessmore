def find_closing_parenthesis(text, start):
    stack = []
    for i in range(start, len(text)):
        if text[i] == "(":
            stack.append(i)
        elif text[i] == ")":
            stack.pop()
            if not stack:
                return i
    return -1  # No matching closing parenthesis found


def test():
    assert find_closing_parenthesis("assert 1 == snapshot(1)", start=15) == len("assert 1 == snapshot(1")
    assert find_closing_parenthesis("assert 1 == snapshot(1())", start=15) == len("assert 1 == snapshot(1()")
    assert find_closing_parenthesis("assert 1 == snapshot(", start=15) == -1


if __name__ == "__main__":
    test()
