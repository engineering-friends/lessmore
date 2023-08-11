import pyperclip


def print_and_copy(text):
    print(text)
    pyperclip.copy(text)
