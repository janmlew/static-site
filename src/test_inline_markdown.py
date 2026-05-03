import unittest

from textnode import TextNode, TextType
from inline_markdown import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold_delimiter(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_italic_delimiter(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_multiple_delimited_segments(self):
        node = TextNode("a `one` b `two` c", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("one", TextType.CODE),
                TextNode(" b ", TextType.TEXT),
                TextNode("two", TextType.CODE),
                TextNode(" c", TextType.TEXT),
            ],
        )

    def test_no_delimiter_in_text(self):
        node = TextNode("plain text with no delimiter", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [TextNode("plain text with no delimiter", TextType.TEXT)],
        )

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("already bold", TextType.BOLD)])

    def test_mixed_node_list(self):
        nodes = [
            TextNode("first ", TextType.TEXT),
            TextNode("inline-bold", TextType.BOLD),
            TextNode(" then `code` here", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("first ", TextType.TEXT),
                TextNode("inline-bold", TextType.BOLD),
                TextNode(" then ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_delimiter_at_start(self):
        node = TextNode("`code` and more", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("code", TextType.CODE),
                TextNode(" and more", TextType.TEXT),
            ],
        )

    def test_delimiter_at_end(self):
        node = TextNode("text ends with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("text ends with ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_whole_text_is_delimited(self):
        node = TextNode("`only code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("only code", TextType.CODE)])

    def test_unclosed_delimiter_raises(self):
        node = TextNode("opens `but never closes", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_unclosed_bold_delimiter_raises(self):
        node = TextNode("starts **but no end", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_empty_input_list(self):
        self.assertEqual(split_nodes_delimiter([], "`", TextType.CODE), [])

    def test_multiple_input_nodes_each_split(self):
        nodes = [
            TextNode("alpha `x` beta", TextType.TEXT),
            TextNode("gamma `y` delta", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("alpha ", TextType.TEXT),
                TextNode("x", TextType.CODE),
                TextNode(" beta", TextType.TEXT),
                TextNode("gamma ", TextType.TEXT),
                TextNode("y", TextType.CODE),
                TextNode(" delta", TextType.TEXT),
            ],
        )

    def test_chained_delimiters(self):
        node = TextNode("mixed **bold** and `code` here", TextType.TEXT)
        after_bold = split_nodes_delimiter([node], "**", TextType.BOLD)
        after_code = split_nodes_delimiter(after_bold, "`", TextType.CODE)
        self.assertEqual(
            after_code,
            [
                TextNode("mixed ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
        )


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_markdown_images_empty_alt(self):
        matches = extract_markdown_images("here ![](https://example.com/x.png)")
        self.assertListEqual([("", "https://example.com/x.png")], matches)

    def test_extract_markdown_images_none(self):
        self.assertListEqual([], extract_markdown_images("no images here"))

    def test_extract_markdown_images_ignores_links(self):
        text = "a [link](https://x.com) is not an image"
        self.assertListEqual([], extract_markdown_images(text))

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_markdown_links_single(self):
        matches = extract_markdown_links("see [docs](https://example.com/docs)")
        self.assertListEqual([("docs", "https://example.com/docs")], matches)

    def test_extract_markdown_links_none(self):
        self.assertListEqual([], extract_markdown_links("no links here"))

    def test_extract_markdown_links_ignores_images(self):
        text = "an ![image](https://x.com/a.png) is not a link"
        self.assertListEqual([], extract_markdown_links(text))

    def test_extract_markdown_links_with_images_in_same_text(self):
        text = (
            "![pic](https://x.com/a.png) and [click](https://www.boot.dev) "
            "and ![other](https://x.com/b.png)"
        )
        self.assertListEqual(
            [("click", "https://www.boot.dev")],
            extract_markdown_links(text),
        )

    def test_extract_markdown_images_with_links_in_same_text(self):
        text = (
            "[a link](https://www.boot.dev) and ![pic](https://x.com/a.png) "
            "and [another](https://example.com)"
        )
        self.assertListEqual(
            [("pic", "https://x.com/a.png")],
            extract_markdown_images(text),
        )


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_single(self):
        node = TextNode("here is ![pic](https://x.com/a.png) inline", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("here is ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" inline", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_at_start(self):
        node = TextNode("![pic](https://x.com/a.png) trailing text", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" trailing text", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_at_end(self):
        node = TextNode("leading text ![pic](https://x.com/a.png)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("leading text ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_only_image(self):
        node = TextNode("![pic](https://x.com/a.png)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("pic", TextType.IMAGE, "https://x.com/a.png")],
            split_nodes_image([node]),
        )

    def test_split_images_adjacent(self):
        node = TextNode(
            "![a](https://x.com/a.png)![b](https://x.com/b.png)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("a", TextType.IMAGE, "https://x.com/a.png"),
                TextNode("b", TextType.IMAGE, "https://x.com/b.png"),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_none_returns_unchanged(self):
        node = TextNode("plain text with no image", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_images_ignores_link(self):
        node = TextNode("a [link](https://www.boot.dev) only", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_images_passes_through_non_text_nodes(self):
        bold_node = TextNode("already bold", TextType.BOLD)
        image_text = TextNode("see ![pic](https://x.com/a.png) here", TextType.TEXT)
        self.assertListEqual(
            [
                bold_node,
                TextNode("see ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" here", TextType.TEXT),
            ],
            split_nodes_image([bold_node, image_text]),
        )

    def test_split_images_empty_input_list(self):
        self.assertListEqual([], split_nodes_image([]))

    def test_split_images_empty_alt(self):
        node = TextNode("before ![](https://x.com/a.png) after", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("before ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" after", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_multiple_input_nodes(self):
        nodes = [
            TextNode("first ![a](https://x.com/a.png) one", TextType.TEXT),
            TextNode("second ![b](https://x.com/b.png) one", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("first ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" one", TextType.TEXT),
                TextNode("second ", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "https://x.com/b.png"),
                TextNode(" one", TextType.TEXT),
            ],
            split_nodes_image(nodes),
        )

    def test_split_images_leaves_links_in_remaining_text(self):
        node = TextNode(
            "see ![pic](https://x.com/a.png) and [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("see ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" and [link](https://www.boot.dev)", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube",
                    TextType.LINK,
                    "https://www.youtube.com/@bootdotdev",
                ),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_single(self):
        node = TextNode("here is [a link](https://www.boot.dev) inline", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("here is ", TextType.TEXT),
                TextNode("a link", TextType.LINK, "https://www.boot.dev"),
                TextNode(" inline", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_at_start(self):
        node = TextNode("[click](https://example.com) trailing", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("click", TextType.LINK, "https://example.com"),
                TextNode(" trailing", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_at_end(self):
        node = TextNode("leading [click](https://example.com)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("leading ", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://example.com"),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_only_link(self):
        node = TextNode("[click](https://example.com)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("click", TextType.LINK, "https://example.com")],
            split_nodes_link([node]),
        )

    def test_split_links_adjacent(self):
        node = TextNode(
            "[a](https://example.com/a)[b](https://example.com/b)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("a", TextType.LINK, "https://example.com/a"),
                TextNode("b", TextType.LINK, "https://example.com/b"),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_none_returns_unchanged(self):
        node = TextNode("plain text with no link", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_ignores_image(self):
        node = TextNode("only ![pic](https://x.com/a.png) here", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_passes_through_non_text_nodes(self):
        italic_node = TextNode("already italic", TextType.ITALIC)
        link_text = TextNode("see [click](https://www.boot.dev) here", TextType.TEXT)
        self.assertListEqual(
            [
                italic_node,
                TextNode("see ", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://www.boot.dev"),
                TextNode(" here", TextType.TEXT),
            ],
            split_nodes_link([italic_node, link_text]),
        )

    def test_split_links_empty_input_list(self):
        self.assertListEqual([], split_nodes_link([]))

    def test_split_links_multiple_input_nodes(self):
        nodes = [
            TextNode("first [a](https://example.com/a) one", TextType.TEXT),
            TextNode("second [b](https://example.com/b) one", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("first ", TextType.TEXT),
                TextNode("a", TextType.LINK, "https://example.com/a"),
                TextNode(" one", TextType.TEXT),
                TextNode("second ", TextType.TEXT),
                TextNode("b", TextType.LINK, "https://example.com/b"),
                TextNode(" one", TextType.TEXT),
            ],
            split_nodes_link(nodes),
        )

    def test_split_links_leaves_image_alone_in_mixed_text(self):
        node = TextNode(
            "see ![pic](https://x.com/a.png) and [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode(
                    "see ![pic](https://x.com/a.png) and ", TextType.TEXT
                ),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            split_nodes_link([node]),
        )

    def test_split_image_then_link_pipeline(self):
        node = TextNode(
            "go ![pic](https://x.com/a.png) then [click](https://www.boot.dev) end",
            TextType.TEXT,
        )
        after_image = split_nodes_image([node])
        result = split_nodes_link(after_image)
        self.assertListEqual(
            [
                TextNode("go ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" then ", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://www.boot.dev"),
                TextNode(" end", TextType.TEXT),
            ],
            result,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_full_example(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_plain_text_only(self):
        self.assertListEqual(
            [TextNode("just plain text", TextType.TEXT)],
            text_to_textnodes("just plain text"),
        )

    def test_only_bold(self):
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)],
            text_to_textnodes("**bold**"),
        )

    def test_only_italic(self):
        self.assertListEqual(
            [TextNode("italic", TextType.ITALIC)],
            text_to_textnodes("_italic_"),
        )

    def test_only_code(self):
        self.assertListEqual(
            [TextNode("snippet", TextType.CODE)],
            text_to_textnodes("`snippet`"),
        )

    def test_only_image(self):
        self.assertListEqual(
            [TextNode("alt", TextType.IMAGE, "https://x.com/a.png")],
            text_to_textnodes("![alt](https://x.com/a.png)"),
        )

    def test_only_link(self):
        self.assertListEqual(
            [TextNode("click", TextType.LINK, "https://example.com")],
            text_to_textnodes("[click](https://example.com)"),
        )

    def test_bold_and_italic_only(self):
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            text_to_textnodes("**bold** and _italic_"),
        )

    def test_image_then_link(self):
        text = "![pic](https://x.com/a.png) and [click](https://www.boot.dev)"
        self.assertListEqual(
            [
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://www.boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_link_then_image(self):
        text = "[click](https://www.boot.dev) before ![pic](https://x.com/a.png)"
        self.assertListEqual(
            [
                TextNode("click", TextType.LINK, "https://www.boot.dev"),
                TextNode(" before ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://x.com/a.png"),
            ],
            text_to_textnodes(text),
        )

    def test_multiple_of_each_inline_type(self):
        text = "**a** and **b** with _x_ and _y_"
        self.assertListEqual(
            [
                TextNode("a", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" with ", TextType.TEXT),
                TextNode("x", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("y", TextType.ITALIC),
            ],
            text_to_textnodes(text),
        )

    def test_empty_string(self):
        self.assertListEqual([], text_to_textnodes(""))

    def test_unclosed_delimiter_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("opens **but never closes")


if __name__ == "__main__":
    unittest.main()
