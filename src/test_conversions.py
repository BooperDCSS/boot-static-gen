import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, TextNode
from conversions import (
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    BlockType,
    markdown_to_html_node,
    header_counter,
    new_text_to_children,
    extract_title
)

class extract_title_test(unittest.TestCase):

    def test_proper_header(self):
        md = """
# This is my header

Here is some text for you to parse

## A second header appears!

But this won't grab it"""
        title_value = extract_title(md)
        self.assertEqual(
            title_value,
            "This is my header"
        )


    def test_two_headers(self):
        md = """
# Danger!

This text has

# Two H1 headers!"""
        with self.assertRaises(Exception):
            extract_title(md)

    def test_no_headers(self):
        md = """
I don't have a real header here.
Not even a double header.

## Though this should throw an error as well"""
        with self.assertRaises(Exception):
            extract_title(md)

    def test_header_after_para(self):
        md = """
Note: I wrote this without giving it a title first. It's intentional.

# I love Autechre

Listen to them."""
        title_value = extract_title(md)
        self.assertEqual(
            title_value,
            "I love Autechre"
        )


class Text_md_to_html(unittest.TestCase):

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

    def test_code_block(self):
        md = """
Here is a code **block** that should not render markdown:

```
Do not render _this_ text as **markdown**
please. I would be upset if you did.
```

The end."""
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            "<div><p>Here is a code <b>block</b> that should not render markdown:</p><pre><code>Do not render _this_ text as **markdown**\nplease. I would be upset if you did.\n</code></pre><p>The end.</p></div>"
        )


    def test_ordered_list(self):
        md = """
1. I love
2. listening to
3. Coil and Autechre

They are two of my _favorite_ bands"""
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>I love</li><li>listening to</li><li>Coil and Autechre</li></ol><p>They are two of my <i>favorite</i> bands</p></div>"
        )

    def test_unordered_list(self):
        md = """
- I love
- listening to
- Coil and Autechre

They are two of my _favorite_ bands"""
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>I love</li><li>listening to</li><li>Coil and Autechre</li></ul><p>They are two of my <i>favorite</i> bands</p></div>"
        )

    def test_header_HTML_only(self):
        md = "#### Hope this works **son**!"
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            "<div><h4>Hope this works <b>son</b>!</h4></div>"
        )

    def test_header_and_para(self):
        md = """
# Header Number 1

I was walking down the street when I noticed some _rude_ dudes
eating pineapple
in the park.
"""
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            "<div><h1>Header Number 1</h1><p>I was walking down the street when I noticed some <i>rude</i> dudes eating pineapple in the park.</p></div>"
        )


    def test_with_quotes(self):
        md = '''
# My header

I like to quote people **a lot**.
Here is a thing someone once said to me:

> "Eat your greens, especially broccoli."

John Balance'''
        md_html_convert = markdown_to_html_node(md)
        html = md_html_convert.to_html()
        self.assertEqual(
            html,
            '<div><h1>My header</h1><p>I like to quote people <b>a lot</b>. Here is a thing someone once said to me:</p><blockquote>"Eat your greens, especially broccoli."</blockquote><p>John Balance</p></div>'
        )

class Test_block_type(unittest.TestCase):
    def test_block_ordlist(self):
        md = "1. Love\n2. Me\n3. Some\n4. Autechre"
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.ORD_LIST)

    def test_failed_ordlist_blocktype(self):
        md = "1. Love\n2. Me\n4. Some\n3. Autechre"
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.PARAGRAPH)

    def test_block_type_header_3(self):
        md = "### A level 3 header"
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.HEADING)

    def test_block_type_code(self):
        md = """```\nThis is some block code\nAcross two lines\nLike this```"""
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.CODE)

    def test_block_type_code(self):
        md = "> Lets make this two quotes\n> For good measure."
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.QUOTE)

    def test_block_type_unord(self):
        md = "- A list of lists\n- To test"
        md_block_type = block_to_block_type(md)
        self.assertEqual(md_block_type, BlockType.UNORD_LIST)

class Test_markdown_blocks(unittest.TestCase):
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

    def test_md_italic_blocks(self):
        md = """_This text begins_
with some italics in _awkward
_places. But it is in good **shape**.

# Header here by some logic


Extra space in the mix."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "_This text begins_\nwith some italics in _awkward\n_places. But it is in good **shape**.",
                "# Header here by some logic",
                "Extra space in the mix."
            ]
        )

class Test_text_to_textnode(unittest.TestCase):

    def test_all_conversion_errors(self):
        original_node = "I [link](www.hi.com) but do not **close my _bold_ `text`."
        with self.assertRaises(ValueError):
            text_to_textnodes(original_node)


    def test_all_types(self):
        original_node = ("This **bold** statement _is_ filled "
            "with [links](www.love.com) to `code` and ![images](www.jpg.com).")
        text_nodes = text_to_textnodes(original_node)
        self.assertListEqual(
            [
                TextNode("This ", TextType.PLAIN_TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" statement ", TextType.PLAIN_TEXT),
                TextNode("is", TextType.ITALIC),
                TextNode(" filled with ", TextType.PLAIN_TEXT),
                TextNode("links", TextType.LINK, "www.love.com"),
                TextNode(" to ", TextType.PLAIN_TEXT),
                TextNode("code", TextType.CODE_TEXT),
                TextNode(" and ", TextType.PLAIN_TEXT),
                TextNode("images", TextType.IMAGE, "www.jpg.com"),
                TextNode(".", TextType.PLAIN_TEXT),
            ],
            text_nodes,
        )

    def test_text_spaces(self):
        original_node = " Wild **and** _crazy_ ![stuff](www.whoa.com)"
        text_nodes = text_to_textnodes(original_node)
        self.assertListEqual(
            [
                TextNode(" Wild ", TextType.PLAIN_TEXT),
                TextNode("and", TextType.BOLD),
                TextNode(" ", TextType.PLAIN_TEXT),
                TextNode("crazy", TextType.ITALIC),
                TextNode(" ", TextType.PLAIN_TEXT),
                TextNode("stuff", TextType.IMAGE, "www.whoa.com"),
            ],
            text_nodes
        )

    def test_plain_text(self):
        original_node = "Hello, I have nothing special inside me."
        text_nodes =  text_to_textnodes(original_node)
        self.assertListEqual(
            [
                TextNode("Hello, I have nothing special inside me.", TextType.PLAIN_TEXT)
            ],
            text_nodes
        )

class Test_Split_IMG_Link(unittest.TestCase):
    
    def test_split_2_links(self):
        node = TextNode(
            "This is text with a [link](~/Workspace/Tired) and a [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN_TEXT),
                TextNode("link", TextType.LINK, "~/Workspace/Tired"),
                TextNode(" and a ", TextType.PLAIN_TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_link_begin(self):
        node = TextNode("[A link](./somefolder/to/hell) at the beginning", TextType.PLAIN_TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("A link", TextType.LINK, "./somefolder/to/hell"),
                TextNode(" at the beginning", TextType.PLAIN_TEXT)
            ],
            new_nodes
        )

    def test_split_2_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN_TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN_TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_image_begin(self):
        node = TextNode(
            "![The image](https://www.hell.com) appears at the beginning here.",
            TextType.PLAIN_TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("The image", TextType.IMAGE, "https://www.hell.com"),
                TextNode(" appears at the beginning here.", TextType.PLAIN_TEXT)
            ],
            new_nodes
        )

    def test_split_image_end(self):
        node = TextNode(

            "Now the image is at the ![end](https://www.phew.com)",
            TextType.PLAIN_TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Now the image is at the ", TextType.PLAIN_TEXT),
                TextNode("end", TextType.IMAGE, "https://www.phew.com")
            ],
            new_nodes
        )

    def test_split_no_images(self):
        node = TextNode(
            "No images here boss",
            TextType.PLAIN_TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("No images here boss", TextType.PLAIN_TEXT)
            ],
            new_nodes
        )

class Test_Extractions(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_md_links(self):
        matches = extract_markdown_links(
            "Here is some text with a [link to Autechre](https://autechre.ws)"
        )
        self.assertListEqual([("link to Autechre", "https://autechre.ws")], matches)


class Test_Split_Nodes(unittest.TestCase):
    def test_split_italics(self):
        old_node = TextNode(
            "There is some _italic text_ in this **string**", TextType.PLAIN_TEXT
        )
        new_nodes = split_nodes_delimiter([old_node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("There is some ", TextType.PLAIN_TEXT),
                TextNode("italic text", TextType.ITALIC),
                TextNode(" in this **string**", TextType.PLAIN_TEXT),
            ],
        )

    def test_split_error(self):
        old_node = TextNode(
            "I forgot to close **my bold delimiter", TextType.PLAIN_TEXT
        )
        with self.assertRaises(ValueError):
            split_nodes_delimiter([old_node], "**", TextType.BOLD)

    def test_split_solo_bold(self):
        old_node = TextNode("bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([old_node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("bold text", TextType.BOLD)])

    def test_split_beginning(self):
        old_node = TextNode("**Bold** from the beginning.", TextType.PLAIN_TEXT)
        new_nodes = split_nodes_delimiter([old_node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Bold", TextType.BOLD),
                TextNode(" from the beginning.", TextType.PLAIN_TEXT),
            ],
        )


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
            "Take me to Autechre", TextType.LINK, "https://autechre.ws"
        )
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.props, {"href": "https://autechre.ws"})
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Take me to Autechre")

    def test_img(self):
        text_node = TextNode(
            "This is Squarepusher", TextType.IMAGE, "https://squarepusher.net/sp.jpg"
        )
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "This is Squarepusher")
        self.assertEqual(
            html_node.props,
            {"src": "https://squarepusher.net/sp.jpg", "alt": "This is Squarepusher"},
        )
