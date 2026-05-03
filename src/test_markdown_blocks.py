import unittest

from markdown_blocks import (
    markdown_to_blocks,
    block_to_block_type,
    BlockType,
    markdown_to_html_node,
    extract_title,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_three_blocks_full_doc(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        self.assertEqual(
            markdown_to_blocks(md),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )

    def test_single_block(self):
        self.assertEqual(
            markdown_to_blocks("just one paragraph"),
            ["just one paragraph"],
        )

    def test_empty_string(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_only_whitespace(self):
        self.assertEqual(markdown_to_blocks("   \n\n   \n\n   "), [])

    def test_excessive_newlines_between_blocks(self):
        md = "first\n\n\n\nsecond\n\n\n\n\nthird"
        self.assertEqual(
            markdown_to_blocks(md),
            ["first", "second", "third"],
        )

    def test_strips_leading_and_trailing_whitespace(self):
        md = "   first  \n\n  second   "
        self.assertEqual(
            markdown_to_blocks(md),
            ["first", "second"],
        )

    def test_preserves_internal_newlines(self):
        md = "line one\nline two\n\nblock two"
        self.assertEqual(
            markdown_to_blocks(md),
            ["line one\nline two", "block two"],
        )

    def test_leading_and_trailing_blank_lines(self):
        md = "\n\nfirst block\n\nsecond block\n\n"
        self.assertEqual(
            markdown_to_blocks(md),
            ["first block", "second block"],
        )

    def test_list_block_kept_together(self):
        md = "- a\n- b\n- c"
        self.assertEqual(markdown_to_blocks(md), ["- a\n- b\n- c"])

    def test_heading_then_paragraph(self):
        md = "# Heading\n\nA paragraph."
        self.assertEqual(
            markdown_to_blocks(md),
            ["# Heading", "A paragraph."],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_h1(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_heading_h6(self):
        self.assertEqual(
            block_to_block_type("###### Smallest Heading"), BlockType.HEADING
        )

    def test_heading_too_many_hashes_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("####### Seven hashes"), BlockType.PARAGRAPH
        )

    def test_heading_missing_space_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("#NoSpace"), BlockType.PARAGRAPH
        )

    def test_code_block(self):
        self.assertEqual(
            block_to_block_type("```\nprint('hi')\n```"),
            BlockType.CODE,
        )

    def test_code_block_with_language(self):
        self.assertEqual(
            block_to_block_type("```python\nprint('hi')\n```"),
            BlockType.CODE,
        )

    def test_code_block_unclosed_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("```\nprint('hi')"), BlockType.PARAGRAPH
        )

    def test_code_block_no_fence_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("just `inline code`"), BlockType.PARAGRAPH
        )

    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type("> a quote"), BlockType.QUOTE)

    def test_quote_multi_line(self):
        self.assertEqual(
            block_to_block_type("> first line\n> second line"), BlockType.QUOTE
        )

    def test_quote_no_space_after_marker(self):
        self.assertEqual(
            block_to_block_type(">no space"), BlockType.QUOTE
        )

    def test_quote_one_line_missing_marker_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("> first\nno marker here"), BlockType.PARAGRAPH
        )

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- only item"), BlockType.ULIST)

    def test_unordered_list_multi_item(self):
        self.assertEqual(
            block_to_block_type("- one\n- two\n- three"), BlockType.ULIST
        )

    def test_unordered_list_missing_space_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("-no space\n-also no space"), BlockType.PARAGRAPH
        )

    def test_unordered_list_one_bad_line_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("- one\nplain"), BlockType.PARAGRAPH
        )

    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_block_type("1. one"), BlockType.OLIST)

    def test_ordered_list_multi_item(self):
        self.assertEqual(
            block_to_block_type("1. one\n2. two\n3. three"), BlockType.OLIST
        )

    def test_ordered_list_starts_at_two_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("2. wrong start\n3. two"), BlockType.PARAGRAPH
        )

    def test_ordered_list_skips_number_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("1. one\n3. skipped"), BlockType.PARAGRAPH
        )

    def test_ordered_list_missing_space_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("1.no space"), BlockType.PARAGRAPH
        )

    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("just a normal paragraph"), BlockType.PARAGRAPH
        )

    def test_paragraph_multi_line(self):
        self.assertEqual(
            block_to_block_type("first line\nsecond line"), BlockType.PARAGRAPH
        )

    def test_paragraph_with_inline_markdown(self):
        self.assertEqual(
            block_to_block_type("This has **bold** and _italic_"),
            BlockType.PARAGRAPH,
        )


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_single_paragraph(self):
        md = "Just a single paragraph."
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><p>Just a single paragraph.</p></div>",
        )

    def test_heading_h1(self):
        self.assertEqual(
            markdown_to_html_node("# Top heading").to_html(),
            "<div><h1>Top heading</h1></div>",
        )

    def test_heading_h6(self):
        self.assertEqual(
            markdown_to_html_node("###### Smallest").to_html(),
            "<div><h6>Smallest</h6></div>",
        )

    def test_heading_with_inline_markdown(self):
        self.assertEqual(
            markdown_to_html_node("## A **bold** heading").to_html(),
            "<div><h2>A <b>bold</b> heading</h2></div>",
        )

    def test_quote_single_line(self):
        self.assertEqual(
            markdown_to_html_node("> a quote").to_html(),
            "<div><blockquote>a quote</blockquote></div>",
        )

    def test_quote_multi_line_joined_with_spaces(self):
        md = "> first line\n> second line\n> third line"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><blockquote>first line second line third line</blockquote></div>",
        )

    def test_quote_with_inline_markdown(self):
        md = "> a quote with **bold** and _italic_"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><blockquote>a quote with <b>bold</b> and <i>italic</i></blockquote></div>",
        )

    def test_unordered_list(self):
        md = "- one\n- two\n- three"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ul><li>one</li><li>two</li><li>three</li></ul></div>",
        )

    def test_unordered_list_with_inline_markdown(self):
        md = "- a **bold** item\n- a _italic_ item\n- a `code` item"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ul><li>a <b>bold</b> item</li><li>a <i>italic</i> item</li><li>a <code>code</code> item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = "1. one\n2. two\n3. three"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ol><li>one</li><li>two</li><li>three</li></ol></div>",
        )

    def test_ordered_list_with_inline_markdown(self):
        md = "1. **first**\n2. _second_\n3. `third`"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ol><li><b>first</b></li><li><i>second</i></li><li><code>third</code></li></ol></div>",
        )

    def test_codeblock_does_not_parse_inline(self):
        md = "```\nraw **not bold** and _not italic_\n```"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><pre><code>raw **not bold** and _not italic_\n</code></pre></div>",
        )

    def test_paragraph_with_link(self):
        md = "click [here](https://www.boot.dev) please"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            '<div><p>click <a href="https://www.boot.dev">here</a> please</p></div>',
        )

    def test_paragraph_with_image(self):
        md = "see ![pic](https://x.com/a.png) here"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            '<div><p>see <img src="https://x.com/a.png" alt="pic"></img> here</p></div>',
        )

    def test_full_document(self):
        md = """# Title

This is a paragraph.

> a quote line

- item one
- item two

1. ordered one
2. ordered two

```
code stays raw
```"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div>"
            "<h1>Title</h1>"
            "<p>This is a paragraph.</p>"
            "<blockquote>a quote line</blockquote>"
            "<ul><li>item one</li><li>item two</li></ul>"
            "<ol><li>ordered one</li><li>ordered two</li></ol>"
            "<pre><code>code stays raw\n</code></pre>"
            "</div>",
        )


class TestExtractTitle(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_strips_trailing_whitespace(self):
        self.assertEqual(extract_title("# Hello   "), "Hello")

    def test_strips_inner_padding(self):
        self.assertEqual(extract_title("#    Spacy   "), "Spacy")

    def test_h1_in_full_document(self):
        md = "Some intro paragraph.\n\n# The Title\n\nMore text."
        self.assertEqual(extract_title(md), "The Title")

    def test_h1_with_inline_markdown_kept_literal(self):
        self.assertEqual(extract_title("# Hello **world**"), "Hello **world**")

    def test_first_h1_when_multiple(self):
        md = "# First\n\nbody\n\n# Second"
        self.assertEqual(extract_title(md), "First")

    def test_no_h1_raises(self):
        with self.assertRaises(Exception):
            extract_title("Just a paragraph with no heading")

    def test_only_h2_raises(self):
        with self.assertRaises(Exception):
            extract_title("## Not an h1")

    def test_only_h6_raises(self):
        with self.assertRaises(Exception):
            extract_title("###### Not an h1")

    def test_empty_string_raises(self):
        with self.assertRaises(Exception):
            extract_title("")

    def test_hash_without_space_raises(self):
        with self.assertRaises(Exception):
            extract_title("#NoSpace")


if __name__ == "__main__":
    unittest.main()
