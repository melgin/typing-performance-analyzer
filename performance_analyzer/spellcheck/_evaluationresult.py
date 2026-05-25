class EvaluationResult:

    def __init__(self, is_correct:bool, effective_rule:str, correct_text:str|None):
        self._is_correct = is_correct
        self._effective_rule = effective_rule
        self._correct_text = correct_text

    @property
    def is_correct(self):
        return self._is_correct

    @property
    def effective_rule(self):
        return self._effective_rule

    @property
    def correct_text(self):
        return self._correct_text
