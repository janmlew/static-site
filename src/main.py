from textnode import TextNode, TextType


def main():
    node = TextNode("This is some anchor text", TextType.LINK_TEXT, "https://www.boot.dev")
    print(node)


main()
