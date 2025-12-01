from performance_analyzer.typing_path.util._characterchangeutil import CharacterChangeUtil
from performance_analyzer.typing_path.util._textchange import TextChangeResult
from performance_analyzer.typing_path.enum import TextChangePosition, TextChangeType
from performance_analyzer.utils.string import StringUtil

class TextChangeCategoryUtil:

    @staticmethod
    def change_type_in_keystroke(before_text, current_text, change) -> (TextChangeType, TextChangePosition):
        before_len = len(before_text)
        current_len = len(current_text)

        if change.removed == '' and change.entered == '':
            return TextChangeType.NO_CHANGE, TextChangePosition.END
        elif before_len < current_len - 1 and current_text.startswith(before_text):
            return TextChangeType.AUTO_COMPLETE, TextChangePosition.END
        elif before_len < current_len and current_text.startswith(before_text):
            return TextChangeType.ENTRY, TextChangePosition.END
        elif before_len > current_len and before_text.startswith(current_text):
            return TextChangeType.DELETE, TextChangePosition.END
        elif before_text.endswith(change.removed) and current_text.endswith(change.entered) and change.index == before_len:
            return TextChangeType.AUTO_CORRECT, TextChangePosition.END
        elif change.removed != '' and change.entered == '':
            return TextChangeType.DELETE, TextChangePosition.INSIDE
        elif change.removed == '' and change.entered != '' and len(change.entered) == 1:
            return TextChangeType.ENTRY, TextChangePosition.INSIDE
        elif change.removed == '' and change.entered != '' and len(change.entered) > 1:
            return TextChangeType.AUTO_COMPLETE, TextChangePosition.INSIDE
        elif change.removed != '' and change.entered != '':
            return TextChangeType.AUTO_CORRECT, TextChangePosition.INSIDE
        else:
            return None, None

    @staticmethod
    def change_type(prev, data) -> (TextChangeType, TextChangeResult):
        current_text = StringUtil.remove_braces(data['current_text'])

        if prev is not None:
            prev_text = StringUtil.remove_braces(prev['current_text'])
        else:
            prev_text = data['before_text']

        change = CharacterChangeUtil.get_text_change(prev_text, current_text)
        change.before = prev_text
        change.current = current_text
        change_type_position = TextChangeCategoryUtil.change_type_in_keystroke(prev_text, current_text, change)
        change.type = change_type_position[0]
        change.position = change_type_position[1]

        return change




