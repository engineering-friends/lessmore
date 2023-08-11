import re


# Search for one or more digits in the given strings
assert re.search(r"\d+", "abc123").group() == "123"
assert re.search(r"\d+", "123").group() == "123"
assert re.search(r"\d+", "123abc").group() == "123"

# Search for one or more digits at the start of the given strings
assert re.search(r"^\d+", "abc123") is None
assert re.search(r"^\d+", "123").group() == "123"
assert re.search(r"^\d+", "123abc").group() == "123"

# Search for strings composed only of digits
assert re.search(r"^\d+$", "abc123") is None
assert re.search(r"^\d+$", "123").group() == "123"
assert re.search(r"^\d+$", "123abc") is None

# Match one or more digits at the start of the given strings
assert re.match(r"\d+", "abc123") is None
assert re.match(r"\d+", "123").group() == "123"
assert re.match(r"\d+", "123abc").group() == "123"

# Match strings composed only of digits
assert re.fullmatch(r"\d+", "abc123") is None
assert re.fullmatch(r"\d+", "123").group() == "123"
assert re.fullmatch(r"\d+", "123abc") is None

# Search for one or more digits at the start of multi-line string
assert re.search(r"^\d+", "abc\n123") is None
assert re.search(r"^\d+", "abc\n123", flags=re.MULTILINE).group() == "123"

# Splitting string based on non-word characters
assert re.split(r"\W+", "Words, words, words.") == ["Words", "words", "words", ""]
assert re.split(r"(\W+)", "Words, words, words.") == ["Words", ", ", "words", ", ", "words", ".", ""]
assert re.split(r"(\W+)", "...words, words...") == ["", "...", "words", ", ", "words", "...", ""]
assert re.split(r"\W+", "Words, words, words.", maxsplit=1) == ["Words", "words, words."]

# Adjusted assertion for splitting string at word boundaries
assert re.split(r"\b", "Words, words, words.") == ["", "Words", ", ", "words", ", ", "words", "."]

# Find all sequences of digits in the given string
assert re.findall(r"\d+", "123 123") == ["123", "123"]

# Find all key=value patterns in the given string
assert re.findall(r"(\w+)=(\d+)", "a=1, b=2") == [("a", "1"), ("b", "2")]

# Replacing sequences of digits with 'abc'
assert re.sub(r"\d+", "abc", "123 123") == "abc abc"
assert re.sub(r"\d+", "abc", "123 123", count=1) == "abc 123"

# Replacing sequences of digits with 'abc' followed by the matched digits
assert re.sub(r"(\d+)", "abc\g<1>", "123 123") == "abc123 abc123"


# Function to wrap matched digits in angle brackets
def f(match):
    found_piece = match.string[match.start() : match.end()]
    return f"<{found_piece}>"


assert re.sub(r"(\d+)", f, "123 123") == "<123> <123>"

# Replace sequences of digits with 'abc' and return tuple of the new string and count of replacements
assert re.subn(r"\d+", "abc", "123 123") == ("abc abc", 2)

# Matching two words separated by a space
m = re.match(r"(\w+) (\w+)", "Isaac Newton, physicist")
assert m.group(0) == "Isaac Newton"
assert m.group(1) == "Isaac"
assert m.group(2) == "Newton"
assert m.group(1, 2) == ("Isaac", "Newton")

# Extracting all matched groups
assert m.groups() == ("Isaac", "Newton")

# Matching two words with named groups
m = re.match(r"(?P<first_name>\w+) (?P<last_name>\w+)", "Malcolm Reynolds")
assert m.groupdict() == {"first_name": "Malcolm", "last_name": "Reynolds"}

# Extracting matched sub-strings using start and end positions
assert m.string == "Malcolm Reynolds"
assert m.string[m.start(1) : m.end(1)] == "Malcolm"
assert m.string[m.start(2) : m.end(2)] == "Reynolds"

# Corrected assertion for span of the entire match
assert m.span(0) == (0, 16)
assert m.span(1) == (0, 7)
assert m.span(2) == (8, 16)
