import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestParentNode(unittest.TestCase):

    def test_no_children(self):
        parent_node = ParentNode("ol", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_multichild(self):
        child_node1 = LeafNode("p", "I am child_node1")
        child_node2 = LeafNode("em", "I am child_node2")
        parent_node = ParentNode("span", [child_node1, child_node2])
        self.assertEqual(
            parent_node.to_html(),
            "<span><p>I am child_node1</p><em>I am child_node2</em></span>"
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

    def test_to_html_child_link(self):
        child_node = LeafNode(
            "a", 
            "Link to Danny Brown", 
            {"href": "https://www.youtube.com/channel/UCi6JfFhYxVxl3_XFVNVVKmQ"})
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            '<div><a href="https://www.youtube.com/channel/UCi6JfFhYxVxl3_XFVNVVKmQ">Link to Danny Brown</a></div>'
        )

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_value_error(self):
        node = LeafNode("a", "")
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_links(self):
        node = LeafNode("a", "Check out Squarepusher", {"href": "https://squarepusher.net"})
        self.assertEqual(node.to_html(), '<a href="https://squarepusher.net">Check out Squarepusher</a>')

    def test_leaf_no_tag(self):
        node = LeafNode("", "No tags here")
        self.assertEqual(node.to_html(), "No tags here")

class TestHTMLNode(unittest.TestCase):
    def test_all_none(self):
        none_node = HTMLNode()
        self.assertIsNone(none_node.props)
        self.assertIsNone(none_node.value)
        self.assertIsNone(none_node.tag)
        self.assertIsNone(none_node.children)

    def test_children_none(self):
        none_children = HTMLNode(
            tag="p",
            value="No children here",
            props={"title": "We have no children here"},
        )
        self.assertIs(none_children.children, None)

    def test_props_value(self):
        node1 = HTMLNode(
            "a", "A link", None, {"href": "https://boot.dev", "target": "_blank"}
        )
        self.assertEqual(
            node1.props_to_html(), ' href="https://boot.dev" target="_blank"'
        )

    def test_all_values(self):
        node = HTMLNode("p", "Test all nodes")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Test all nodes")
        self.assertIs(node.children, None)
        self.assertIs(node.props, None)

    def test_tagval_none(self):
        node = HTMLNode(children=[], props={"href": "https://booper.me"})
        self.assertIs(node.tag, None)
        self.assertIs(node.value, None)

    def test_repr(self):
        node1 = HTMLNode(
            "p",
            "I like Autechre",
            None,
            {"href": "https://autechre.ws", "target": "_blank"},
        )
        self.assertEqual(
            node1.__repr__(),
            "HTMLNode(p, I like Autechre, children=None, {'href': 'https://autechre.ws', 'target': '_blank'})"
        )
