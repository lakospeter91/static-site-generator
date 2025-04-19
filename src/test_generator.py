import unittest

from generator import extract_title, generate_pages_recursive


class TestGenerator(unittest.TestCase):
    def test_extract_title(self):
        md = "# Hello"
        title = extract_title(md)
        self.assertEqual(title, "Hello")

    def test_extract_title_multi_line(self):
        md = """
some text
#  Hello  
some more text
"""
        title = extract_title(md)
        self.assertEqual(title, "Hello")

    def test_extract_title_not_found(self):
        md = """
some text
  Hello  
some more text
"""

        with self.assertRaises(Exception) as e:
            extract_title(md)
        self.assertEqual(str(e.exception), "Markdown has no title")


if __name__ == "__main__":
    unittest.main()