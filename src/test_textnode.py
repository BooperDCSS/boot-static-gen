import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("I like Autechre", TextType.BOLD, "https://autechre.ws")
        node2 = TextNode(
            "I like Autechre",
            TextType.BOLD,
        )
        self.assertNotEqual(node, node2)

    def test_diff_type(self):
        node = TextNode("I like coffee", TextType.CODE_TEXT)
        node2 = TextNode("I like coffee", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_diff_content(self):
        node = TextNode("I have tinnitus", TextType.PLAIN_TEXT)
        node2 = TextNode("I want whiskey", TextType.PLAIN_TEXT)
        self.assertNotEqual(node, node2)

    def test_diff_url(self):
        node = TextNode("A", TextType.LINK, "https://boot.dev")
        node2 = TextNode("A", TextType.LINK, "https://boot.dev")
        self.assertEqual(node, node2)


if __name__ == "__main__":
    unittest.main()
