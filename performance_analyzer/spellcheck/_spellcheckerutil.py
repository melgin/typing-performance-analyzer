import re
from collections import deque
from typing import Set, Dict, List
from performance_analyzer.spellcheck._filereader import FileReader
from utils.string import StringUtil

REPLACE_ALL_REPETITIONS = re.compile(r"(.)\1+")
REPLACE_MORE_THAN_TWICE_REPETITIONS = re.compile(r"(.)\1+")

TURKISH_CHARACTER_MAP: Dict[str, str] = {
    'i': 'ı',
    'u': 'ü',
    'o': 'ö',
    'c': 'ç',
    's': 'ş',
    'g': 'ğ',
    'I': 'İ',
    'U': 'Ü',
    'O': 'Ö',
    'C': 'Ç',
    'S': 'Ş',
    'G': 'Ğ',
}

CHARACTERS_NEXT_TO_SPACE = {'v', 'b', 'n', 'm', 'V', 'B', 'N', 'M', '.'}

VOWELS = "aeıioöuü"
TURKISH_VOWELS = set("aeıioöuüAEIİOÖUÜ")

ONES = {
    0: "sıfır", 1: "bir", 2: "iki", 3: "üç", 4: "dört",
    5: "beş", 6: "altı", 7: "yedi", 8: "sekiz", 9: "dokuz"
}

TENS = {
    10: "on", 20: "yirmi", 30: "otuz", 40: "kırk",
    50: "elli", 60: "altmış", 70: "yetmiş",
    80: "seksen", 90: "doksan"
}

UNIT_PATTERN = re.compile(r"(cm|mm|MHz|KHz|kg|g|m|km|ml|L|Hz)$", re.IGNORECASE)

ORDINAL_MAP = {
    "bir": "birinci",
    "iki": "ikinci",
    "üç": "üçüncü",
    "dört": "dördüncü",
    "beş": "beşinci",
    "altı": "altıncı",
    "yedi": "yedinci",
    "sekiz": "sekizinci",
    "dokuz": "dokuzuncu",
    "on": "onuncu"
}

post_transitions_tr = FileReader.read_json_file('resources', 'tr-post-transitions.json')
pre_transitions_tr = FileReader.read_json_file('resources', 'tr-pre-transitions.json')
mid_transitions_tr = FileReader.read_json_file('resources', 'tr-mid-transitions.json')
suffixes_tr = FileReader.read_csv_file('tr-suffixes.csv')

frequent_mistakes_tr = FileReader.read_json_file('resources', 'tr-frequent-mistakes.json')
frequent_mistakes_en = FileReader.read_json_file('resources', 'en-frequent-mistakes.json')

postfixes_tr = FileReader.read_csv_file('tr-postfixes.csv')

class SpellCheckerUtil:

    @staticmethod
    def remove_all_repetitions(word: str) -> str:
        """
        Replaces consecutive repeated characters with a single occurrence.
        """
        return REPLACE_ALL_REPETITIONS.sub(r"\1", word)

    @staticmethod
    def get_repetition_variations(word: str) -> set[str]:
        """
        Generates all possible variations of the word by progressively
        removing repeated characters (after reducing repetitions > 2 to 2).
        """
        result = set()
        #result.add(word)

        if word == SpellCheckerUtil._remove_repeating_character(word):
            return result

        removed_repeats_more_than_twice = REPLACE_MORE_THAN_TWICE_REPETITIONS.sub(r"\1\1", word)

        if len(removed_repeats_more_than_twice) > 15:
            result.add(removed_repeats_more_than_twice)
            return result

        candidates = deque()
        candidates.append(removed_repeats_more_than_twice)
        result.add(removed_repeats_more_than_twice)

        while candidates:
            candidate = candidates.popleft()

            for i in range(len(candidate)):
                removed = SpellCheckerUtil._remove_repeating_character_once_after(candidate, i)

                if removed != candidate and removed not in result:
                    result.add(removed)
                    candidates.append(removed)

        return result

    @staticmethod
    def _remove_repeating_character(word: str) -> str:
        """
        Removes only the first detected consecutive repeating character.
        """
        prev = None
        found = False
        result = []

        for current in word:
            if current != prev or found:
                result.append(current)
            else:
                found = True
            prev = current

        return "".join(result)

    @staticmethod
    def _remove_repeating_character_once_after(word: str, j: int) -> str:
        """
        Removes a single repeating character starting from index j.
        """
        prev = None
        found = False
        result = []

        # Copy characters before index j
        result.extend(word[:j])

        # Process from index j onward
        for current in word[j:]:
            if current != prev or found:
                result.append(current)
            else:
                found = True
            prev = current

        return "".join(result)

    @staticmethod
    def get_turkish_character_variation(word: str, is_partial=False) -> Set[str]:
        """
        Generates all Turkish character variations of the given word.
        """
        variations: Set[str] = set()
        #variations.add(word)

        if word.count('BILIR') > 0:
            variations.add(word.replace('BILIR', 'BİLİR'))

        # If contains punctuation, return as-is
        if any(p in word for p in [".", ",", "(", ")"]):
            return variations

        valid_characters: Set[str] = set()

        # If not partial and word already contains Turkish-specific characters, return original
        if not is_partial:
            for value in TURKISH_CHARACTER_MAP.values():
                if value in word:
                    return variations

        # Determine which base characters are valid for replacement
        for key, value in TURKISH_CHARACTER_MAP.items():
            if value not in word:
                valid_characters.add(key)

        candidates: List[str] = [word]

        while candidates:
            candidate = candidates.pop(0)

            for i, current in enumerate(candidate):
                if current in valid_characters and current in TURKISH_CHARACTER_MAP:
                    new_one = (
                            candidate[:i]
                            + TURKISH_CHARACTER_MAP[current]
                            + candidate[i + 1:]
                    )

                    if new_one not in variations:
                        candidates.append(new_one)

                    if 'BİLIR' in new_one or 'BILİR' in new_one or 'bilır' in new_one or 'bılir' in new_one:
                        continue

                    variations.add(new_one)

        return variations


    @staticmethod
    def _to_lower_tr(text: str) -> str:
        tr_map = str.maketrans({
            "I": "ı",
            "İ": "i"
        })
        return text.translate(tr_map).lower()

    @staticmethod
    def get_dialect_variations(word: str) -> Set[str]:
        result: Set[str] = set()
        #result.add(word)

        lower_tr = SpellCheckerUtil._to_lower_tr(word)

        for key, values in post_transitions_tr.items():
            if lower_tr.endswith(key):
                base = lower_tr[:-len(key)]
                for alternative in values:
                    result.add(base + alternative)

        for key, values in mid_transitions_tr.items():
            if key in lower_tr and not lower_tr.endswith(key):
                for alternative in values:
                    if alternative not in lower_tr:
                        result.add(lower_tr.replace(key, alternative))

        for key, values in pre_transitions_tr.items():
            if lower_tr.startswith(key):
                for alternative in values:
                    replaced = lower_tr.replace(key, alternative, 1)
                    result.update(SpellCheckerUtil.get_dialect_variations(replaced))

        lower = word.lower()

        for key, values in post_transitions_tr.items():
            if lower.endswith(key):
                base = lower_tr[:-len(key)]
                for alternative in values:
                    result.add(base + alternative)

        for key, values in mid_transitions_tr.items():
            if key in lower and not lower.endswith(key):
                for alternative in values:
                    if alternative not in lower:
                        result.add(lower.replace(key, alternative))

        for key, values in pre_transitions_tr.items():
            if lower.startswith(key):
                for alternative in values:
                    replaced = lower_tr.replace(key, alternative, 1)
                    result.update(SpellCheckerUtil.get_dialect_variations(replaced))

        return result

    @staticmethod
    def get_neologism_variations(word: str) -> Set[str]:
        result: Set[str] = set()
        for item in suffixes_tr:
            if word.endswith(item):
                result.add(word[:-len(item)])

        return result

    @staticmethod
    def get_frequent_mistake_equivalent(word: str, lang: str) -> str|None:
        equivalent = None
        if lang == "en":
            equivalent = frequent_mistakes_en.get(word)
        elif lang == "tr":
            equivalent = frequent_mistakes_tr.get(word)

        return equivalent

    from typing import Set

    @staticmethod
    def get_phonetic_substitution_variations(word: str, lang: str) -> Set[str]:
        variations: Set[str] = set()
        #variations.add(word)

        lower = SpellCheckerUtil._to_lower_tr(word)

        # Direct replacements
        variations.add(lower.replace("q", "k"))
        variations.add(lower.replace("sh", "ş"))
        variations.add(lower.replace("ch", "ç"))
        variations.add(lower.replace("gh", "ğ"))
        variations.add(lower.replace("ph", "f"))
        variations.add(lower.replace("ei", "eği"))
        variations.add(lower.replace("io", "iyo"))
        variations.add(lower.replace("ey", "eğ"))
        variations.add(lower.replace("uşu", "u"))
        variations.add(lower.replace("üşü", "ü"))
        variations.add(lower.replace("işi", ""))
        variations.add(lower.replace("işi", "i"))
        variations.add(lower.replace("ışı", ""))
        variations.add(lower.replace("ışı", "ı"))
        variations.add(lower.replace("wamke", "vam"))

        if "e" not in lower and "3" in lower:
            variations.add(lower.replace("3", "e"))

        variations.add(lower.replace("$", "ş"))
        variations.add(lower.replace("w", "v"))

        # Ending rules
        if lower.endswith("ğ"):
            variations.add(lower[:-1])

        if lower.endswith("s"):
            variations.add(lower[:-1] + "z")

        if lower.startswith("arkis"):
            variations.add("arkadas" + lower[5:])

        if lower.endswith("que"):
            variations.add(lower[:-3] + "k")

        if lower.endswith("yolla"):
            variations.add(lower[:-5] + "yorlar")

        if lower.endswith("idim"):
            variations.add(lower[:-4] + "tim")

        for suffix in ["cık", "cik", "çık", "çik"]:
            if lower.endswith(suffix):
                variations.add(lower[:-3])

        if lower.endswith("ib"):
            variations.add(lower[:-2] + "ip")

        if lower.endswith("ıb"):
            variations.add(lower[:-2] + "ıp")

        for suffix in ["ıskom", "iskom", "ışkom", "işkom"]:
            if lower.endswith(suffix):
                variations.add(lower.replace(suffix, "ım"))
                variations.add(lower.replace(suffix, "am"))

        if lower.endswith("koşum"):
            variations.add(lower.replace("koşum", "ke"))

        if "ei" in lower:
            variations.add(lower.replace("ei", "eği"))

        if "ıo" in lower:
            variations.add(lower.replace("ıo", "ıyor"))

        if lower.startswith("new"):
            variations.add("yeni" + lower[3:])

        if lower.startswith("Büsküvi"):
            variations.add("Bisküvi" + lower[7:])

        if lower.startswith("büsküvi"):
            variations.add("bisküvi" + lower[7:])

        if "io" in lower:
            variations.add(lower.replace("io", "ıyor"))

        if lower.startswith("g"):
            variations.add("k" + lower[1:])

        if lower.startswith("şeyap"):
            variations.add("yap" + lower[5:])

        if lower.startswith("bidaki"):
            variations.add("dahaki" + lower[6:])

        if lower.startswith("biss"):
            variations.add(lower[3:])

        if lower == "bebitolar":
            variations.add("bebekler")

        if lower == "minnağın":
            variations.add("miniğin")

        if lower == "minnak":
            variations.add("minik")

        if word.endswith("oş") or word.endswith("üş"):
            variations.add(lower[:-2] + "e")
            variations.add(lower[:-2] + "a")

        if word.endswith("cım") or word.endswith("cim"):
            variations.add(lower[:-3])

        if "s" in word:
            variations.add(lower.replace("s", "z"))

        if "d" in word and lang == "en":
            variations.add(lower.replace("d", "t"))

        if word.endswith("s"):
            variations.add(lower[:-1])

        # Repetition removal (recursive)
        rep_removed = SpellCheckerUtil.remove_all_repetitions(lower)

        if lower != rep_removed:
            variations.update(SpellCheckerUtil.get_phonetic_substitution_variations(rep_removed, lang))

        if word.lower() in variations:
            variations.remove(word.lower())

        return variations

    @staticmethod
    def get_proper_noun_variations(word: str) -> Set[str]:
        variations: Set[str] = set()
        if "'" not in word:
            proper_noun_case = StringUtil.convert_to_proper_case(word)

            for i in range(len(proper_noun_case) - 1, 1, -1):
                main = proper_noun_case[:i]
                suffix = proper_noun_case[i:]

                if suffix in suffixes_tr:
                    variations.add(main + "'" + suffix)
        else:
            variations.add(word.replace("'", ""))

        return variations

    @classmethod
    def _number_to_text(cls, n: int) -> str:
        if n < 10:
            return ONES[n] + ' '
        if n < 100:
            if n in TENS:
                return TENS[n]
            return TENS[(n // 10) * 10] + " " + ONES[n % 10]
        if n < 1000:
            h = n // 100
            r = n % 100
            prefix = "yüz" if h == 1 else ONES[h] + " yüz"
            return prefix if r == 0 else prefix + " " + cls._number_to_text(r)
        if n < 1_000_000:
            t = n // 1000
            r = n % 1000
            prefix = "bin" if t == 1 else cls._number_to_text(t) + " bin"
            return prefix if r == 0 else prefix + " " + cls._number_to_text(r)
        return str(n)

    @classmethod
    def _make_ordinal(cls, text: str):
        last_word = text.split()[-1]
        if last_word in ORDINAL_MAP:
            return text.rsplit(last_word, 1)[0] + ORDINAL_MAP[last_word]
        return text + "ıncı"

    @classmethod
    def _decimal_to_text(cls, left: str, right: str) -> str:
        if right == "5":
            return str(int(left)) + " buçuk"
        if right == "50":
            return str(int(left)) + " buçuk"
        if right == "25":
            return str(int(left)) + " çeyrek"
        return (
                str(int(left))
                + " virgül "
                + " ".join(ONES[int(d)] for d in right)
        )

    @classmethod
    def _soften_four(cls, word: str, suffix: str) -> str:
        if word.endswith("dört") and suffix and suffix[0] in VOWELS:
            return word[:-1]  # dört → dörd
        return word

    @classmethod
    def _normalize_token(cls, token: str):
        # Skip math expressions
        if re.search(r"[=^+]", token):
            return token

        # Range handling
        range_match = re.match(r"^(\d+)-(\d+)(.*)", token)
        if range_match:
            a, b, suffix = range_match.groups()
            return (
                    str(int(a))
                    + " ile "
                    + str(int(b))
                    + " "
                    + suffix
            ).strip()

        # Decimal
        decimal_match = re.match(r"^(\d+)\.(\d+)(.*)", token)
        if decimal_match:
            left, right, suffix = decimal_match.groups()
            base = cls._decimal_to_text(left, right)
            return base + suffix

        # Ordinal like 2.si
        ordinal_match = re.match(r"^(\d+)\.(.*)", token)
        if ordinal_match:
            number, suffix = ordinal_match.groups()
            base = cls._make_ordinal(cls._number_to_text(int(number)))
            return base + suffix

        # Pure number + suffix
        number_match = re.match(r"^(\d+)(.*)", token)
        if number_match:
            number, suffix = number_match.groups()

            base = str(int(number))
            base = cls._soften_four(base, suffix)

            # Apostrophe case
            if suffix in ["'s", "s"]:
                return base

            # Units
            if UNIT_PATTERN.search(suffix):
                return base + " " + suffix

            return base + ' ' + suffix

        return token

    @staticmethod
    def normalize_numeric_text(text: str):
        tokens = re.split(r"(\s+)", text)
        return "".join(
            SpellCheckerUtil._normalize_token(t) if not t.isspace() else t
            for t in tokens
        )

    @staticmethod
    def get_misspelled_conjunction_variants(word) -> set[str]:
        variants = set()
        for postfix in postfixes_tr:
            if word.endswith(postfix):
                fixed = word[:-len(postfix)]
                if fixed != '' :
                    variants.add(fixed + " " + postfix)
        return variants

    @staticmethod
    def is_valid_conjunction(word) -> set[str]:
        return word in postfixes_tr

    @staticmethod
    def get_invalid_space_variations(word: str) -> set[str]:
        result = set()

        if len(word) < 6:
            return result

        for i in range(1, len(word) - 1):
            c = word[i]

            if c in CHARACTERS_NEXT_TO_SPACE:
                first = word[:i]
                second = word[i + 1:]

                if SpellCheckerUtil._is_valid(first) and SpellCheckerUtil._is_valid(second):
                    result.add(first + " " + second)

        return result

    @staticmethod
    def _is_valid(segment: str) -> bool:
        if len(segment) <= 1:
            return False

        if SpellCheckerUtil._starts_with_numeric(segment):
            return True

        repetition_removed = SpellCheckerUtil.remove_all_repetitions(segment)

        if len(repetition_removed) <= 1:
            return False

        vowel_count = 0
        non_vowel_count = 0

        for c in repetition_removed:
            if SpellCheckerUtil._is_vowel(c):
                vowel_count += 1
            else:
                non_vowel_count += 1

        return vowel_count > 0 and non_vowel_count > 0

    @staticmethod
    def _starts_with_numeric(text: str) -> bool:
        """
        Returns True if the string starts with a digit.
        """
        if not text:
            return False

        return text[0].isdigit()

    @staticmethod
    def _is_vowel(char: str) -> bool:
        """
        Returns True if character is a Turkish vowel.
        """
        return char in TURKISH_VOWELS

    @staticmethod
    def get_missing_space_variations(word: str) -> set[str]:
        result = set()

        if len(word) < 6 or '.' in word:
            return result

        for i in range(2, len(word) - 2):
            first = word[:i]
            second = word[i:]

            if SpellCheckerUtil._is_valid(first) and SpellCheckerUtil._is_valid(second):
                result.add(first + " " + second)

        return result

    @staticmethod
    def get_character_order_error_variations(word: str) -> set[str]:
        result = set()

        if len(word) <= 2:
            return result

        for i in range(0, len(word) - 1):
            result.add(word[:i] + word[i + 1] + word[i] + word[i + 2:])

        return result

    @staticmethod
    def get_text_difference(a: str, b: str) -> list[str]:
        """
        Return the two input strings with their longest common suffix removed.

        If the strings share no trailing characters, both are returned unchanged.
        """
        # Find the length of the longest common suffix
        i = 0
        min_len = min(len(a), len(b))
        while i < min_len and a[-(i + 1)] == b[-(i + 1)]:
            i += 1

        # Slice off the common suffix from each string
        if i == 0:
            return [a, b]
        return [a[:-i], b[:-i]]
