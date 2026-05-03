from enum import Enum

from htmlnode import ParentNode
from inline_markdown import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ULIST = "unordered_list"
    OLIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    return [block.strip() for block in blocks if block.strip()]


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].endswith("```"):
        return BlockType.CODE

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.ULIST

    if all(line.startswith(f"{i + 1}. ") for i, line in enumerate(lines)):
        return BlockType.OLIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def paragraph_to_html_node(block):
    text = " ".join(block.split("\n"))
    return ParentNode("p", text_to_children(text))


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    text = block[level + 1:]
    return ParentNode(f"h{level}", text_to_children(text))


def code_to_html_node(block):
    inner = block[3:]
    if "\n" in inner:
        inner = inner.split("\n", 1)[1]
    if inner.endswith("```"):
        inner = inner[:-3]
    code_child = text_node_to_html_node(TextNode(inner, TextType.TEXT))
    return ParentNode("pre", [ParentNode("code", [code_child])])


def quote_to_html_node(block):
    cleaned_lines = []
    for line in block.split("\n"):
        stripped = line[1:]
        if stripped.startswith(" "):
            stripped = stripped[1:]
        cleaned_lines.append(stripped)
    text = " ".join(cleaned_lines)
    return ParentNode("blockquote", text_to_children(text))


def ulist_to_html_node(block):
    items = []
    for line in block.split("\n"):
        items.append(ParentNode("li", text_to_children(line[2:])))
    return ParentNode("ul", items)


def olist_to_html_node(block):
    items = []
    for i, line in enumerate(block.split("\n")):
        prefix_len = len(f"{i + 1}. ")
        items.append(ParentNode("li", text_to_children(line[prefix_len:])))
    return ParentNode("ol", items)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.ULIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.OLIST:
        return olist_to_html_node(block)
    raise ValueError(f"Unsupported block type: {block_type}")


def markdown_to_html_node(markdown):
    children = [block_to_html_node(block) for block in markdown_to_blocks(markdown)]
    return ParentNode("div", children)


def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("No h1 header found in markdown")
