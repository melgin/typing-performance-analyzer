from typing import List, Dict
from performance_analyzer.utils.string import StringUtil

class SessionUtil:

    @staticmethod
    def split_into_sessions(data: List[Dict]) -> List[List[Dict]]:
        """
        Starts a new session when:
        - current item's before_text == ""
        - previous item's current_text != ""

        Returns:
            List of sessions (list of lists)
        """

        if not data:
            return []

        sessions = []
        current_session = [data[0]]

        for i in range(1, len(data)):
            prev_item = data[i - 1]
            current_item = data[i]

            new_session = (
                    current_item["before_text"] == ""
                    and StringUtil.remove_braces(prev_item["current_text"]) != ""
            )

            if new_session:
                sessions.append(current_session)
                current_session = [current_item]
            else:
                current_session.append(current_item)

        # Add last session
        if current_session:
            sessions.append(current_session)

        return sessions

    @staticmethod
    def get_final_text(data_list) -> str:
        current_text = data_list[len(data_list) - 1]['current_text']
        return StringUtil.remove_braces(current_text)

    @staticmethod
    def get_initial_text(data_list) -> str:
        return data_list[0]['before_text']

    @staticmethod
    def get_text_len(data_list) -> int:
        return len(SessionUtil.get_final_text(data_list)) - len(SessionUtil.get_initial_text(data_list))

    @staticmethod
    def get_overall_len(sessions: List[Dict]) -> int:
        text_length = 0
        for session in sessions:
            text_length += SessionUtil.get_text_len(session)
        return text_length
