import unittest

from performance_analyzer.utils.string import StringUtil


class TestStringUtil(unittest.TestCase):

    def test_remove_braces(self):
        self.assertEqual('test', StringUtil.remove_braces('[test]'))
        self.assertEqual('test', StringUtil.remove_braces('[test'))
        self.assertEqual('test', StringUtil.remove_braces('test]'))
        self.assertEqual('test', StringUtil.remove_braces('test'))
        self.assertEqual('te]st', StringUtil.remove_braces('te]st'))
        self.assertEqual(']test[', StringUtil.remove_braces(']test['))

if __name__ == '__main__':
    unittest.main()
