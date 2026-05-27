from performance_analyzer.typing_path.enum import TextChangePosition, TextChangeType
from performance_analyzer.typing_path._typingactivity import TypingActivityHelper
from performance_analyzer.typing_path.util import TextChangeCategoryUtil
from utils.session import SessionUtil


class TypingPathCalculator:

    def __init__(self, data_list:list):
        self.data_list = data_list
        self._sessions = SessionUtil.split_into_sessions(data_list)
        self._path = self.data_list[0]['before_text']
        self._real_entered_text_length = 0
        self._correction_msd = 0
        self._edit_correction_list = []
        self._auto_completes = []
        self._typing_activities = []

    @property
    def path(self):
        return self._path

    def calculate(self) -> None:
        for session in self._sessions:
            typing_activity = TypingActivityHelper()
            prev = None
            prev_current_text = None

            for index in range(len(session)):
                data = session[index]
                change = TextChangeCategoryUtil.change_type(prev, data)
                current_text = change.current

                if typing_activity.is_activity_changed(change):
                    typing_activity.append_current_activity(change, prev_current_text, index)

                if change.position == TextChangePosition.END:
                    if change.type == TextChangeType.INSERT:
                        typing_activity.add_to_end_of_current_activity(change.entered)
                    elif change.type == TextChangeType.AUTO_COMPLETE:
                        typing_activity.add_to_end_of_current_activity(change.entered)
                    elif change.type == TextChangeType.DELETE:
                        typing_activity.add_to_start_of_current_activity(change.removed)
                    elif change.type == TextChangeType.AUTO_CORRECT:
                        typing_activity.append_current_activity(change, prev_current_text, index)
                        typing_activity.append_current_change(change, index)
                elif change.position == TextChangePosition.INSIDE:
                    if change.type == TextChangeType.INSERT:
                        typing_activity.add_to_end_of_current_activity(change.entered)
                    elif change.type == TextChangeType.AUTO_COMPLETE:
                        typing_activity.add_to_end_of_current_activity(change.entered)
                    elif change.type == TextChangeType.DELETE:
                        typing_activity.add_to_start_of_current_activity(change.removed)
                    elif change.type == TextChangeType.AUTO_CORRECT:
                        typing_activity.append_current_activity(change, prev_current_text, index)
                        typing_activity.append_current_change(change, index)

                typing_activity.set_previous_activity_type(change)
                prev_current_text = current_text
                prev = data

            typing_activity.append_current_activity(None, prev_current_text, len(self.data_list))
            self._typing_activities.append(typing_activity)

    def detect_edit_operations(self):
        for typing_activity in self._typing_activities:
            typing_activity.detect_edit_operations()

    def get_revised_text_length(self):
        revised_text_len = 0
        for typing_activity in self._typing_activities:
            revised_text_len += typing_activity.get_revised_text_length()
        return revised_text_len

    def auto_correction_msd(self):
        auto_correction_msd = 0
        for typing_activity in self._typing_activities:
            auto_correction_msd += typing_activity.auto_correction_msd()
        return auto_correction_msd

    def corrected_error_msd(self):
        corrected_error_msd = 0
        for typing_activity in self._typing_activities:
            corrected_error_msd += typing_activity.corrected_error_msd()
        return corrected_error_msd

    def print_path(self):
        for typing_activity in self._typing_activities:
            typing_activity.print_activity()
