from performance_analyzer.typing_path.util._textchange import TextChangeResult

class CharacterChangeUtil:

    @staticmethod
    def get_text_change(before_text:str, current_text:str) -> TextChangeResult:
        return CharacterChangeUtil._get_text_change(0, before_text, current_text)

    @staticmethod
    def _get_text_change(index: int, before_text:str, current_text:str) -> TextChangeResult:
        if before_text == '' or current_text == '':
            return TextChangeResult(index, before_text, current_text)
        elif before_text[0] == current_text[0]:
            return CharacterChangeUtil._get_text_change(index + 1, before_text[1:], current_text[1:])
        elif before_text[-1] == current_text[-1]:
            return CharacterChangeUtil._get_text_change(index, before_text[:-1], current_text[:-1])
        else:
            return TextChangeResult(index, before_text, current_text)
