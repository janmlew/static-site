import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_not_eq_texttypes(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq_url_none_default(self):
        node = TextNode("anchor", TextType.LINK)
        node2 = TextNode("anchor", TextType.LINK, None)
        self.assertEqual(node, node2)

    def test_not_eq_different_text(self):
        node = TextNode("first", TextType.TEXT)
        node2 = TextNode("second", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_url(self):
        node = TextNode("anchor", TextType.LINK, "https://www.boot.dev")
        node2 = TextNode("anchor", TextType.LINK, "https://example.com")
        self.assertNotEqual(node, node2)

    def test_not_eq_url_none_vs_set(self):
        node = TextNode("anchor", TextType.LINK)
        node2 = TextNode("anchor", TextType.LINK, "https://www.boot.dev")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()