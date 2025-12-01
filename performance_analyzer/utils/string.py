import re

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

class StringUtil:

    @staticmethod
    def remove_braces(text:str) -> str:
        """
        Removes the braces ([ and ]) around the text.

        It only changes the text if the first character is [ or the last character is ].

        :param text:
        :return:
        """
        if text.startswith('['):
            text = text[1:]

        if text.endswith(']'):
            text = text[:-1]

        return text
