import unittest

from performance_analyzer.spellcheck import SpellChecker


class TestSpellChecker(unittest.TestCase):

    def test_check_spelling_with_numeric_typo(self):
        test = SpellChecker.evaluate('1.dwn', 'tr')
        self.assertEqual('1.den', test.correct_text)
        self.assertFalse(test.is_correct)

    def test_check_spelling_with_numeric_valid_word(self):
        test = SpellChecker.evaluate('1.si', 'tr')
        self.assertEqual('1.si', test.correct_text)
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('5buçukta', 'tr')
        self.assertEqual('5buçukta', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_abbreviation(self):
        test = SpellChecker.evaluate('TBMM', 'tr')
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('tbmm', 'tr')
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_deasciification(self):
        test = SpellChecker.evaluate('cuce', 'tr')
        self.assertTrue(test.correct_text)

        test = SpellChecker.evaluate('kucuk', 'tr')
        self.assertEqual('küçük', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_repetition(self):
        test = SpellChecker.evaluate('merhabaaaa', 'tr')
        self.assertTrue(test.is_correct)
        self.assertEqual('merhaba', test.correct_text)

        test = SpellChecker.evaluate('Eveeeet', 'tr')
        self.assertEqual('Evet', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_dialect_and_accent(self):
        test = SpellChecker.evaluate('yapcam', 'tr')
        self.assertEqual('yapacağım', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_frequent_mistake(self):
        test = SpellChecker.evaluate('antreman', 'tr')
        self.assertEqual('antrenman', test.correct_text)
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('tommorow', 'en')
        self.assertEqual('tomorrow', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_fat_finger_problem(self):
        test = SpellChecker.evaluate('latee', 'en')
        self.assertFalse(test.is_correct)

        test = SpellChecker.evaluate('olmazss', 'tr')
        self.assertEqual('olmazsa', test.correct_text)
        self.assertFalse(test.is_correct)

    def test_check_spelling_with_text_speak(self):
        test = SpellChecker.evaluate('canışkom', 'tr')
        self.assertEqual('canım', test.correct_text)
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('hackledim', 'tr')
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('tmm', 'tr')
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_invalid_space(self):
        test = SpellChecker.evaluate('kitapnkurdu', 'tr')
        self.assertEqual('kitap kurdu', test.correct_text)
        self.assertFalse(test.is_correct)

        test = SpellChecker.evaluate('aldıkgeldik', 'tr')
        self.assertEqual('aldık geldik', test.correct_text)
        self.assertFalse(test.is_correct)

        test = SpellChecker.evaluate('Ama.yine', 'tr')
        self.assertEqual('Ama yine', test.correct_text)
        self.assertFalse(test.is_correct)

        test = SpellChecker.evaluate('var.Bunların', 'tr')
        self.assertEqual('var. Bunların', test.correct_text)
        self.assertTrue(test.is_correct)

        test = SpellChecker.evaluate('olurmu', 'tr')
        self.assertEqual('olur mu', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_proper_noun(self):
        test = SpellChecker.evaluate('Ankaradayım', 'tr')
        self.assertEqual('Ankara\'dayım', test.correct_text)
        self.assertTrue(test.is_correct)

    def test_check_spelling_with_valid_word(self):
        test = SpellChecker.evaluate('test', 'tr')
        self.assertTrue(test.is_correct)

if __name__ == '__main__':
    unittest.main()
