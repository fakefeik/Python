import unittest
import html_parse


class TestClass(unittest.TestCase):
    def test_html_remove(self):
        self.assertEqual("", html_parse.get_correct_html("<d></d>"))
        self.assertEqual("<b></b>", html_parse.get_correct_html("<b></b>"))
        self.assertEqual("asd", html_parse.get_correct_html("<br/>asd<br/>"))

    def test_html_correct(self):
        self.assertEqual("<b></b>", html_parse.get_correct_html("<b>"))
    
    def test_html_closing(self):
        self.assertEqual("<sad>", html_parse.correct_closing_symbols("<sad"))
        self.assertEqual("<sad<abc>>", html_parse.correct_closing_symbols("<sad<abc"))
        
    def test_html_has_any_text(self):
        self.assertTrue(html_parse.has_any_text("abc"))
        self.assertTrue(html_parse.has_any_text("<b>sdasf</b>"))
        self.assertFalse(html_parse.has_any_text("<b></b>"))
        self.assertFalse(html_parse.has_any_text("<asd>"))

if __name__ == '__main__':
    unittest.main()