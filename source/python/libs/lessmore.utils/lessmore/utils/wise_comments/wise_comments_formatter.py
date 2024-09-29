import re

from lessmore.utils.wise_comments.config.config import config
from sortedcontainers import SortedList


# todo later: doc properly [@marklidenberg]


class WiseCommentsFormatter:
    def __init__(self, single_comments, multi_comments=None, username=None, is_username_required=False):
        self.single_comments = single_comments  # like ['#']
        self.multi_comments = multi_comments or []  # like [('"""', '"""'), ("'''", "'''")]

        self.username = username or config.get("username")

        assert self.username or (
            not self.username and not is_username_required
        ), "Specify username (usually in os.environs['WISE_COMMENTS_USERNAME'])"

        if self.username and self.username[0] != "@":
            self.username = "@" + self.username

    @staticmethod
    def _repeat_symbol_split(symbol, count, split_number=3):
        # symbol="-", count=10, split_count=3 -> "--- --- --- -"

        return " ".join(
            [" ".join([symbol * split_number] * (count // split_number)), symbol * (count % split_number)]
        ).strip()

    def _format_steps(self, text, single_comment):
        def substitutor(match, text):
            # - Skip case when previous symbol is not "\"

            if match.span()[0] >= 2 and text and text[match.span()[0] - 2] == "\\":
                return text[match.span()[0] : match.span()[1]]

            # - Extract

            s1, dashes, s2, text = match.groups()  # sample comment: (s1) # (s2) (dashes, like ----) (s3) (text)

            # - Strip

            text = text.strip()

            # - Make title

            text = text[0].upper() + text[1:]

            # - Remove trailing dots if only one

            text = re.sub(r"[\.]*$", "", text)

            # - Return final string

            return f'\n{s1}{single_comment} {WiseCommentsFormatter._repeat_symbol_split("-", len(dashes))} {text.strip()}\n\n'

        empty_line = r"(?:[ ]*\n)"
        pattern = rf"^{empty_line}*([ ]*){re.escape(single_comment)} (-+)([ ]+)([^\n]+){empty_line}*"
        return re.sub(pattern, lambda match: substitutor(match, text=text), text, flags=re.MULTILINE)

    def _format_sections(self, text, single_comment):
        def substitutor(match):
            # - Process general case

            s1, s2, brackets, s3, text = match.groups()  # sample comment: (s1) # (s2) (brackets, like [[[) (s3) (text)
            brackets = brackets.replace(" ", "")

            text = text.strip()

            # - Make title

            text = text[0].upper() + text[1:]

            # - Remove trailing closing brackets

            text = re.sub(r"([\] ]*)$", "", text)

            # - Remove trailing dots if only one

            text = re.sub(r"[\.]*$", "", text)

            # - Remove closing brackets

            bracket = r"\]"
            text = re.sub(rf"[{bracket}]*", "", text)
            return f'\n{s1}{single_comment} {WiseCommentsFormatter._repeat_symbol_split("[", len(brackets))}{text.strip()}{WiseCommentsFormatter._repeat_symbol_split("]", len(brackets))}\n\n'

        empty_line = r"(?:[ ]*\n)"
        bracket = r"\["
        brackets = rf"({bracket}[{bracket} ]*)"
        pattern = rf"^{empty_line}*([ ]*){re.escape(single_comment)}([ ]*){brackets}([ ]*)([^\n]+){empty_line}*"

        return re.sub(pattern, substitutor, text, flags=re.MULTILINE)

    def _format_multi_line_comments(self, text, multi_comment):
        def substitutor(match):
            # - Extract

            (
                s1,
                multi_comment_start,
                text,
                multi_comment_stop,
            ) = match.groups()  # sample comment: (s1) (comment_symbol_start) (text) (comment_symbol_stop)

            # - Strip

            text = text.strip()

            # - Remove trailing dots if only one

            text = re.sub(r"[\.]*$", "", text)

            # - Make title

            text = text[0].upper() + text[1:]

            lines = text.split("\n")
            lines = [line.strip() for line in lines]

            if len(lines) >= 2:
                lines = [multi_comment_start] + lines + [multi_comment_stop]
            else:
                lines = [multi_comment_start + lines[0] + multi_comment_stop]

            # - Append tabulation

            lines = [s1 + line for line in lines]
            return "\n".join(lines)

        pattern = rf"""^([ ]*)({re.escape(multi_comment[0])})(.*?)({re.escape(multi_comment[1])})(?:[ ]*)$"""
        return re.sub(pattern, substitutor, text, flags=re.MULTILINE | re.DOTALL)

    def _format_single_line_comments(self, text, single_comment):
        def substitutor(match):
            # - Extract

            s1, text = match.groups()  # sample comment: (s1) # (text)

            # - Remove trailing dots if only one

            text = re.sub(r"[\.]*$", "", text)

            # - Return final string

            return f"{s1}#{text}"

        pattern = rf"^([ ]*){re.escape(single_comment)}([^\n]+)"
        return re.sub(pattern, substitutor, text, flags=re.MULTILINE)

    def _format_squeezed_new_lines(self, text, single_comment=None, multi_comment=None):
        assert single_comment or multi_comment

        patterns = []

        if single_comment:
            patterns.append(rf"^([ ]*){re.escape(single_comment)}([^\n]+)")

        if multi_comment:
            patterns.append(rf"""^([ ]*)({re.escape(multi_comment[0])})(.*?)({re.escape(multi_comment[1])})""")

        def is_empty_or_comment_line(text):
            if "\n" in text:
                return False

            return re.sub(r"\s", "", text)[:1] in ["", "#"]

        # - Split lines

        lines = text.split("\n")

        # - Collect line infos

        line_infos = []
        current_start = 0
        for line in lines:
            line_info = {}
            line_info["line"] = line
            line_info["start"] = current_start
            line_info["end"] = current_start + len(line) + 1
            current_start += len(line) + 1
            line_infos.append(line_info)

        line_infos = SortedList(line_infos, key=lambda value: value["start"])

        # - Calculate indexes of lines that need new line inserted

        new_line_indexes = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.MULTILINE | re.DOTALL):
                # - Find line before

                comment_start = match.span()[0]
                comment_finish = match.span()[1]
                line_before_info_index = line_infos.bisect_left({"start": comment_start}) - 1

                if line_before_info_index == -1:
                    line_before = None
                else:
                    line_before = line_infos[line_before_info_index]["line"]

                # - Skip case when previous symbol is not "\"

                if line_before and line_before[-1] == "\\":
                    continue

                # - Find line after

                line_after_info_index = line_infos.bisect_right({"start": comment_finish})

                if line_after_info_index == len(line_infos):
                    line_after = None
                else:
                    line_after = line_infos[line_after_info_index]["line"]
                if line_before and line_after:
                    # Lines before and after present

                    if not is_empty_or_comment_line(line_before) and not is_empty_or_comment_line(line_after):
                        # fmt: off
                        """
                        Squeezed comment example
                        
                        some code here
                        # squeezed pre-comment example
                        some code here
                        """
                        # fmt: on
                        new_line_indexes.append(line_before_info_index)

        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if i in new_line_indexes:
                new_lines.append("")

        return "\n".join(new_lines)

    def _format_todos(self, text, single_comment):
        def substitute(match):
            # - Extract

            spaces, status, text, tags = (value if value else "" for value in match.groups())

            # - Format matches

            text = text.strip()

            # Remove trailing dots if only one

            text = re.sub(r"[\.]*$", "", text)

            status = status or "later"

            # - Format tags

            tags = tags[1:-1]  # remove square brackets
            tags = tags.split(",")
            tags = [tag.strip() for tag in tags if tag]
            tags = sorted(tags, key=lambda value: "@" != value[0])

            tags = [tag if not re.match(r"[a-zA-Z0-9]", tag[0]) else "#" + tag for tag in tags]
            if self.username and (not tags or "@" != tags[0][0]):
                # There is no a username in tags

                tags = [self.username] + tags

            # - Return

            tags_text = " [{}]".format(", ".join(tags)) if tags else ""
            return f"{spaces}{single_comment} todo {status}: {text}{tags_text}"

        # - Build todo pattern

        spaces = r"[ ]*"
        status = r"(?:next)|(?:later)|(?:maybe)"
        colon = r"\:"
        text_till_end_of_line = "[^\n\\[\\]]*"
        todo = r"[tT][oO][dD][oO]"
        word = r"[\S]+"
        words = rf"{word}(?:,(?:{spaces}){word}(?:{spaces}))*(?:{spaces})"
        tags = rf"\[{words}\]"
        pattern = rf"({spaces}){single_comment}(?:{spaces})(?:{todo})(?:{spaces})({status})?(?:{spaces})(?:{colon})?({text_till_end_of_line})({tags})?(?:{spaces})"

        return re.sub(pattern, substitute, text)

    def _mark_non_formatted_lines(self, text, single_comment):
        """Prefix non-formatted lines with 'WISE_FORMATTING_OFF: '"""

        is_formatting_on = True
        new_lines = []
        for line in text.split("\n"):
            spaces = r"(?:[ ]*)"
            single_comment_prefix = rf"{spaces}{re.escape(single_comment)}{spaces}"
            if re.search(rf"^{single_comment_prefix}fmt:{spaces}off", line):
                is_formatting_on = False

            if re.search(rf"{single_comment_prefix}fmt:{spaces}skip", line) or not is_formatting_on:
                new_lines.append("WISE_FORMATTING_OFF: " + line)
            else:
                new_lines.append(line)

            if re.search(rf"^{single_comment_prefix}fmt:{spaces}on", line):
                is_formatting_on = True
        return "\n".join(new_lines)

    def _unmark_non_formatted_lines(self, text):
        """Remove 'WISE_FORMATTING_OFF: ' prefixes"""

        return re.sub("^WISE_FORMATTING_OFF: ", "", text, flags=re.MULTILINE)

    def format(self, text):
        text = self._mark_non_formatted_lines(text, single_comment=self.single_comments[0])
        for single_comment in self.single_comments:
            text = self._format_steps(text, single_comment=single_comment)

            # text = self._format_sections(text, single_comment=single_comment)
            text = self._format_single_line_comments(text, single_comment=single_comment)
            text = self._format_squeezed_new_lines(text, single_comment=single_comment)

            # todo later: reimplement to not use for common projects + add date
            # text = self._format_todos(text, single_comment=single_comment)

        # todo later: there are many bugs with multi comments. Need fixing later [@marklidenberg]
        # for multi_comment in self.multi_comments:
        #     text = self._format_multi_line_comments(text, multi_comment=multi_comment)
        #     text = self._format_squeezed_new_lines(text, multi_comment=multi_comment)

        text = self._unmark_non_formatted_lines(text)
        return text
