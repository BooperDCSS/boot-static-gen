import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, TextNode
from text_to_html import text_node_to_html_node

class Test_Text_to_HTML_node(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN_TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        text_node = TextNode("Make me bold", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Make me bold")

    def test_link(self):
        text_node = TextNode(
            "Take me to Autechre",
            TextType.LINK,
            "https://autechre.ws")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.props, {"href": "https://autechre.ws"})
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Take me to Autechre")

    def test_img(self):
        text_node = TextNode(
            "This is Squarepusher",
            TextType.IMAGE,
            "https://squarepusher.net/sp.jpg")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://squarepusher.net/sp.jpg", "alt": "This is Squarepusher"})
