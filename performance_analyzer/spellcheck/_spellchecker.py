import sys

from phunspell import Phunspell
from performance_analyzer.spellcheck._evaluationresult import EvaluationResult
from performance_analyzer.spellcheck._filereader import FileReader
from performance_analyzer.spellcheck._spellcheckerutil import SpellCheckerUtil
from utils.string import StringUtil
from typing import Dict

hunspell_tr = Phunspell('tr_TR')
hunspell_en = Phunspell('en_US')

text_speak_tr = FileReader.read_csv_file('tr-text-speak-glossary.csv')
text_speak_en = FileReader.read_csv_file('en-text-speak-glossary.csv')

abbreviations_tr = FileReader.read_csv_file('tr-abbr.csv')
addresses_tr = FileReader.read_csv_file('tr-addresses.csv')
names_tr = FileReader.read_csv_file('tr-names.csv')

DEBUG = False

SPACE = ' '
TR = 'tr'
EN = 'en'

class SpellChecker:

    @staticmethod
    def check_spelling(word:str) -> bool:
        return hunspell_tr.lookup(word)

    @classmethod
    def evaluate(cls, word:str, lang:str, depth:int=0) -> EvaluationResult:
        if cls._is_correct(word, lang):
            return EvaluationResult(True, "dictionary", None)

        if cls._is_case_alternative_correct(word, lang):
            return EvaluationResult(True, "case-alternative", None)

        suggestion_map: Dict[str, str] = {}

        suggestion = cls._suggest(word, lang, suggestion_map)
        if suggestion is not None and StringUtil.adjacent_string_distance(suggestion, word) == 0:
            if depth == 0:
                (is_found, is_valid, correct_text) = cls._is_deasciification(word, lang, suggestion_map, depth)
                if is_found:
                    return EvaluationResult(is_valid, "deasciification", correct_text)
            return EvaluationResult(False, "suggestion", suggestion)

        (is_found, is_valid, correct_text) = cls._is_dialect_or_accent(word, lang, depth, suggestion_map)
        if is_found:
            return EvaluationResult(is_valid, "dialect-or-accent", correct_text)

        (is_valid, correct_text) = cls._is_repeating_characters(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "repeating-characters", correct_text)

        if lang == TR and cls._is_correct(word, EN):
            return EvaluationResult(True, "english", None)

        (is_found, is_valid, correct_text) = cls._is_deasciification(word, lang, suggestion_map, depth)
        if is_found:
            return EvaluationResult(is_valid, "deasciification", correct_text)

        (is_valid, correct_text) = cls._is_phonetic_substitution(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "phonetic-substitution", correct_text)

        (is_valid, correct_text) = cls._is_misspelled_conjunction(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "misspelled-conjunction", correct_text)

        (is_valid, correct_text) = cls._is_frequent_mistake(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "frequent-mistake", correct_text)

        (is_found, is_valid, correct_text) = cls._is_character_order_error(word, lang, depth)
        if is_found:
            return EvaluationResult(is_valid, "character-order", correct_text)

        (is_valid, correct_text) = cls._is_proper_noun(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "proper-noun", correct_text)

        (is_valid, correct_text) = cls._is_neologism(word, lang, suggestion_map, depth)
        if is_valid:
            return EvaluationResult(is_valid, "neologism", correct_text)

        if depth == 0:
            (is_found, is_valid, correct_text) = cls._is_invalid_space(word, lang, depth)
            if is_found:
                return EvaluationResult(is_valid, "invalid-space", correct_text)

            (is_found, is_valid, correct_text) = cls._is_missing_space(word, lang, depth)
            if is_found:
                return EvaluationResult(is_valid, "missing-space", correct_text)

            (is_found, is_valid, correct_text) = cls._is_numeric_case(word, lang, suggestion_map, depth, suggestion)
            if is_found:
                return EvaluationResult(is_valid, "numeric-case", correct_text)

        return EvaluationResult(False, "none", cls._suggest(word, lang, suggestion_map))

    @staticmethod
    def suggest(word:str):
        return hunspell_tr.suggest(word)

    @classmethod
    def _is_correct(cls, word:str, lang:str) -> bool:
        if lang == TR:
            if word in abbreviations_tr or word in names_tr or word in addresses_tr or word in text_speak_tr:
                return True

            return hunspell_tr.lookup(word)
        elif lang == EN:
            if word in text_speak_en:
                return True

            return hunspell_en.lookup(word)
        else:
            return False

    @classmethod
    def _is_case_alternative_correct(cls, word:str, lang:str) -> bool:
        """
        Tokens that become valid after converting to lower, upper, and proper noun cases
        :param word:
        :param lang:
        :return:
        """
        lower = StringUtil.convert_to_lower_case(word)
        if lower != word and cls._is_correct(lower, lang):
            return True

        upper = StringUtil.convert_to_upper_case(word)
        if upper != word and cls._is_correct(upper, lang):
            return True

        proper = StringUtil.convert_to_proper_case(word)
        if proper != word and cls._is_correct(proper, lang):
            return True

        return False

    @classmethod
    def _suggest(cls, word:str, lang:str, suggestion_map:Dict[str, str]) -> str | None:
        suggestion = suggestion_map.get(word)

        if suggestion is not None:
            return suggestion

        if lang == TR:
            suggestion = cls._get_closest_suggestion(hunspell_tr.suggest(word), word)
            if suggestion is not None:
                suggestion_map.update({ word : suggestion })

            return suggestion
        elif lang == EN:
            suggestion = cls._get_closest_suggestion(hunspell_en.suggest(word), word)
            if suggestion is not None:
                suggestion_map.update({ word : suggestion })
            return suggestion
        else:
            return None

    @classmethod
    def _get_closest_suggestion(cls, items, word):
        adjacent_list = []
        other_list = []

        for item in items:
            if item is not None:
                if SPACE in item:
                    conjunction = item.split(SPACE)[1]
                    if SpellCheckerUtil.is_valid_conjunction(conjunction):
                        return item

                dist = StringUtil.adjacent_string_distance(item, word)
                if dist == 0:
                    adjacent_list.append(item)
                else:
                    other_list.append(item)

        closest = None
        closest_distance = sys.maxsize

        if len(adjacent_list) > 0:
            for item in adjacent_list:
                dist = StringUtil.string_distance(item, word)
                if dist < closest_distance:
                    closest = item
                    closest_distance = dist

            return closest
        else:
            for item in other_list:
                dist = StringUtil.adjacent_string_distance(item, word)
                if dist < closest_distance:
                    closest = item
                    closest_distance = dist

            return closest

    @classmethod
    def _is_dialect_or_accent(cls, word, lang, depth, suggestion_map: Dict[str, str]):
        """
        Checks tokens that are written in informal forms in text speak and become valid after applying dialectical and accent transitions
        :param word:
        :param lang:
        :return:
        """
        if lang != TR:
            return False, False, None

        candidates = SpellCheckerUtil.get_dialect_variations(word)

        cls._debug_candidates('dialect candidates', candidates, depth)

        for candidate in candidates:
            if cls._is_correct(candidate, lang):
                return True, True, candidate

            result = cls.evaluate(candidate, lang, depth + 1)
            if result.effective_rule == 'suggestion' and result.correct_text is not None:
                return True, False, result.correct_text

        return False, False, None

    @classmethod
    def _is_repeating_characters(cls, word, lang, suggestion_map: Dict[str, str], depth) -> (bool, str|None):
        """
        Checks tokens that become valid after removing repetitive characters, that are generally used for expressing emotions
        :param word:
        :param lang:
        :return:
        """
        candidates = SpellCheckerUtil.get_repetition_variations(word)

        cls._debug_candidates('repeating candidates', candidates, depth)

        if len(candidates) <= 1:
            # no repetitive pattern
            return False, None

        suggestion = cls._suggest(word, lang, suggestion_map)
        if suggestion is not None and StringUtil.adjacent_string_distance(suggestion, word) == 0:
            # repetition is related to a typo
            return False, None

        for candidate in candidates:
            if candidate == suggestion:
                return True, candidate
            elif word != candidate and cls._is_case_alternative_correct(candidate, lang):
                return True, candidate

        return False, None

    @classmethod
    def _is_deasciification(cls, word, lang, suggestion_map: Dict[str, str], depth:int):
        """
        Checks tokens that become valid after applying deasciification, to detect use of "i", "o", "u", "c", "g", and "s"
        instead of "ı", "ö", "ü", "ç", "ğ", and "ş" characters
        :param word:
        :param lang:
        :return:
        """
        if lang != TR:
            return False, False, None

        candidates = SpellCheckerUtil.get_turkish_character_variation(word)

        cls._debug_candidates('deascii candidates', candidates, depth)

        for candidate in candidates:
            if cls._is_correct(candidate, lang):
                return True, True, candidate

            (is_valid, correct_text) = cls._is_repeating_characters(candidate, lang, suggestion_map, depth)
            if is_valid:
                return True, True, correct_text

            suggestion = cls._suggest(candidate, lang, suggestion_map)

            if suggestion is not None:
                if suggestion != candidate and suggestion in candidates:
                    return True, True, suggestion

                if StringUtil.adjacent_string_distance(suggestion, word) == 0:
                    return True, False, suggestion

        return False, False, None

    @classmethod
    def _is_proper_noun(cls, word, lang, suggestion_map: Dict[str, str], depth:int):
        """
        Checks proper nouns with missing apostrophes, generally ignored in text speak
        :param word:
        :param lang:
        :return:
        """
        candidates = SpellCheckerUtil.get_proper_noun_variations(word)

        cls._debug_candidates('proper noun candidates', candidates, depth)

        for candidate in candidates:
            if cls._is_correct(candidate, lang):
                return True, candidate

        return False, None

    @classmethod
    def _is_phonetic_substitution(cls, word, lang, suggestion_map: Dict[str, str], depth:int):
        """
        Checks tokens that are intentionally corrupted by replacing some characters with phonetically similar forms or nonalphabetic characters
        :param word:
        :param lang:
        :return:
        """
        candidates = SpellCheckerUtil.get_phonetic_substitution_variations(word, lang)

        cls._debug_candidates('phonetic candidates', candidates, depth)

        suggestion = cls._suggest(word, lang, suggestion_map)
        if suggestion is not None and StringUtil.adjacent_string_distance(suggestion, word) == 0:
            # repetition is related to a typo
            return False, None

        for candidate in candidates:
            if cls._is_correct(candidate, lang) and StringUtil.adjacent_string_distance(candidate, word) != 0:
                return True, candidate
            (if_found, is_valid, correct_text) = cls._is_deasciification(candidate, lang, suggestion_map, 0)
            if if_found and is_valid:
                return True, correct_text

        return False, None

    @classmethod
    def _is_misspelled_conjunction(cls, word, lang, suggestion_map: Dict[str, str], depth:int) -> (bool, str|None):
        """
        Checks tokens that ends with a frequently misspelled conjunction
        :param word:
        :param lang:
        :return:
        """
        if lang != TR:
            return False, None

        variants = SpellCheckerUtil.get_misspelled_conjunction_variants(word)

        cls._debug_candidates('misspelled conjunction candidates', variants, depth)

        for variant in variants:
            root = variant.split(SPACE)[0]
            if cls._is_case_alternative_correct(root, lang):
                return True, variant

            (is_valid, correct_text) = cls._is_phonetic_substitution(root, lang, suggestion_map, depth)
            if is_valid:
                return True, correct_text

        return False, None

    @classmethod
    def _is_frequent_mistake(cls, word, lang, suggestion_map: Dict[str, str], depth:int):
        """
        Checks frequent spelling mistakes
        :param word:
        :param lang:
        :return:
        """
        equivalent = SpellCheckerUtil.get_frequent_mistake_equivalent(word, lang)

        if equivalent is not None:
            cls._debug_candidates('frequent candidates', {equivalent}, depth)
            return True, equivalent

        return False, None

    @classmethod
    def _is_neologism(cls, word, lang, suggestion_map: Dict[str, str], depth:int):
        """
        Checks non-Turkish words followed by a Turkish suffix

        Examples: hacklemek, resetlemek

        :param word:
        :param lang:
        :return:
        """
        if lang != TR:
            return False, None

        candidates = SpellCheckerUtil.get_neologism_variations(word)

        cls._debug_candidates( 'neologism candidates', candidates, depth)

        for variation in candidates:
            if cls._is_correct(variation, EN):
                return True, variation

        return False, None

    @classmethod
    def _is_numeric_case(cls, word, lang, suggestion_map: Dict[str, str], depth:int, suggestion) -> (bool, bool, str|None):
        """
        Normalizes numeric text and checks if it is valid.

        Examples: 1.si, 1den, 20cm

        :param word: word to be normalized and checked
        :param lang: text language
        :return: tuple (is_normalized, is_valid, corrected_text)
         - is_normalized: whether given word is normalized by converting numeric statements to text
         - is_valid: whether given word is valid after normalization
         - corrected_text: normalized text (numeric to text)
        """
        normalized = SpellCheckerUtil.normalize_numeric_text(word)
        if normalized == word:
            return False, False, None

        cls._debug_candidates( 'numeric candidates', {normalized}, depth)

        text_diff = SpellCheckerUtil.get_text_difference(word, normalized)

        tokens = normalized.split()

        if len(tokens) < 2:
            if cls._is_correct(normalized, lang):
                return True, True, word
        else:
            correct_list = []
            incorrect_list = []
            not_found_list = []
            corrected_text = ''
            for token in tokens:
                result = cls.evaluate(token, lang, depth + 1)
                if result.is_correct:
                    correct_list.append(token)
                    corrected_text += token
                elif result.effective_rule is not None and result.effective_rule != '' and result.effective_rule != 'none':
                    print(token, result.effective_rule)
                    incorrect_list.append(token)
                    corrected_text += result.correct_text
                else:
                    not_found_list.append(token)
                    if result.correct_text is not None:
                        corrected_text += result.correct_text

            if len(incorrect_list) == 0 and len(not_found_list) == 0 and len(correct_list) > 0:
                return True, True, word
            elif len(incorrect_list) > 0 and len(not_found_list) == 0 and len(correct_list) >= 0:
                corrected_text = corrected_text.strip()
                corrected_text = SpellChecker._get_closest_suggestion({corrected_text, cls._suggest(corrected_text, lang, suggestion_map), suggestion}, normalized)
                return True, False, corrected_text.replace(text_diff[1], text_diff[0])

        corrected_text = SpellChecker._get_closest_suggestion({cls._suggest(normalized, lang, suggestion_map), suggestion}, normalized)
        if corrected_text is None:
            return False, False, corrected_text
        return True, False, corrected_text.replace(text_diff[1], text_diff[0])

    @classmethod
    def _is_invalid_space(cls, word, lang, depth:int) -> (bool, bool, str|None):
        """
        """
        candidates = SpellCheckerUtil.get_invalid_space_variations(word)

        cls._debug_candidates( 'invalid space candidates', candidates, depth)

        if len(candidates) == 0:
            return False, False, None

        for candidate in candidates:
            words = candidate.split()
            first = words[0]
            second = words[1]

            first_result = cls.evaluate(first, lang, depth + 1)
            if first_result.is_correct:
                second_result = cls.evaluate(second, lang, depth + 1)

                if second_result.is_correct:
                    if second[0].isupper():
                        return True, True, first + ". " + second

                    return True, False, (first_result.correct_text or first) + SPACE + (second_result.correct_text or second)

        return False, False, None

    @classmethod
    def _is_missing_space(cls, word, lang, depth:int) -> (bool, bool, str|None):
        """
        """
        candidates = SpellCheckerUtil.get_missing_space_variations(word)

        cls._debug_candidates( 'missing space candidates', candidates, depth)

        if len(candidates) == 0:
            return False, False, None

        for candidate in candidates:
            words = candidate.split()
            first = words[0]
            second = words[1]

            first_result = cls.evaluate(first, lang, depth + 1)
            if first_result.is_correct:
                second_result = cls.evaluate(second, lang, depth + 1)

                if second_result.is_correct:
                    return True, False, (first_result.correct_text or first) + SPACE + (second_result.correct_text or second)

        return False, False, None

    @classmethod
    def _is_character_order_error(cls, word, lang, depth:int) -> (bool, bool, str|None):
        """
        """
        candidates = SpellCheckerUtil.get_character_order_error_variations(word)

        cls._debug_candidates('character order error candidates', candidates, depth)

        if len(candidates) == 0:
            return False, False, None

        for candidate in candidates:
            if cls._is_correct(candidate, lang):
                return True, False, candidate
            else:
                items = SpellCheckerUtil.get_turkish_character_variation(candidate)

                for item in items:
                    if cls._is_correct(item, lang):
                        return True, False, candidate

            suggestion = cls._suggest(candidate, lang, {})
            if suggestion is not None and StringUtil.adjacent_string_distance(suggestion, candidate) == 0:
                return True, False, suggestion

        (is_valid, correct_text) = cls._is_misspelled_conjunction(word, lang, {}, depth)
        if is_valid:
            return True, False, correct_text

        return False, False, None

    @staticmethod
    def _debug(*args):
        if DEBUG:
            print(*args)

    @staticmethod
    def _debug_candidates(description:str, candidates:set[str], depth:int):
        if DEBUG and len(candidates) > 0:
            if depth == 0:
                print(' ->', description + ':', candidates)
            else:
                print((depth - 1) * '  ', ' ->', description + ':', candidates)

