import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple(self):
        node = HTMLNode(
            "a",
            "Click me",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_props_to_html_single(self):
        node = HTMLNode("p", "hello", None, {"class": "greeting"})
        self.assertEqual(node.props_to_html(), ' class="greeting"')

    def test_props_to_html_none(self):
        node = HTMLNode("p", "hello")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty(self):
        node = HTMLNode("p", "hello", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_to_html_raises(self):
        node = HTMLNode("p", "hello")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com">Click me!</a>',
        )

    def test_leaf_to_html_h1(self):
        node = LeafNode("h1", "A Heading")
        self.assertEqual(node.to_html(), "<h1>A Heading</h1>")

    def test_leaf_to_html_no_tag_returns_raw_text(self):
        node = LeafNode(None, "just some raw text")
        self.assertEqual(node.to_html(), "just some raw text")

    def test_leaf_to_html_no_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_to_html_empty_string_value_allowed(self):
        node = LeafNode("img", "", {"src": "https://x.com/a.png", "alt": "pic"})
        self.assertEqual(
            node.to_html(),
            '<img src="https://x.com/a.png" alt="pic"></img>',
        )

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        parent_node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            parent_node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_props(self):
        parent_node = ParentNode(
            "a",
            [LeafNode(None, "Click me!")],
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            parent_node.to_html(),
            '<a href="https://www.google.com" target="_blank">Click me!</a>',
        )

    def test_to_html_deeply_nested(self):
        deepest = LeafNode("em", "deep")
        level3 = ParentNode("span", [deepest])
        level2 = ParentNode("p", [level3, LeafNode(None, " trailing")])
        level1 = ParentNode("section", [level2, LeafNode("p", "after")])
        self.assertEqual(
            level1.to_html(),
            "<section><p><span><em>deep</em></span> trailing</p><p>after</p></section>",
        )

    def test_to_html_sibling_parents(self):
        left = ParentNode("li", [LeafNode(None, "one")])
        right = ParentNode("li", [LeafNode(None, "two")])
        ul = ParentNode("ul", [left, right])
        self.assertEqual(ul.to_html(), "<ul><li>one</li><li>two</li></ul>")

    def test_to_html_no_children_raises(self):
        parent_node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_none_children_raises(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_no_tag_raises(self):
        parent_node = ParentNode(None, [LeafNode("p", "hi")])
        with self.assertRaises(ValueError):
            parent_node.to_html()


if __name__ == "__main__":
    unittest.main()
