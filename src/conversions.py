import re
from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, TextNode

# Creating HTML-related nodes from TextNodes...

def text_node_to_html_node(text_node):
    if text_node.text_type not in TextType:
        raise ValueError("HTML element not yet supported")
    if text_node.text_type == TextType.PLAIN_TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE_TEXT:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

# converts Markdown text to a list of TextNodes using the split_nodes functions

def text_to_textnodes(text):

    original_text = TextNode(text, TextType.PLAIN_TEXT)
    bold_split = split_nodes_delimiter([original_text], "**", TextType.BOLD)
    italic_split = split_nodes_delimiter(bold_split, "_", TextType.ITALIC)
    code_split = split_nodes_delimiter(italic_split, "`", TextType.CODE_TEXT)
    image_split = split_nodes_image(code_split)
    link_split = split_nodes_link(image_split)

    return link_split

# converts blocks of Markdown text to individual strings

def markdown_to_blocks(md):
    blocks = []
    
    split_doc =  md.split("\n\n") # only split on two newline chars
    for line in split_doc:
        if line == "":
            continue
        line = line.strip() # guard check for leading or trailing whitespace or newlines
        blocks.append(line)
    return blocks



# split_nodes functions
# Splitting plain text nodes into component nodes with correct enum membership
# delimiter covers plain, bold, italic, and code text

def split_nodes_delimiter(nodes, delimiter, text_type):
    new_nodes = []

    for node in nodes:
        if node.text_type != TextType.PLAIN_TEXT:
            new_nodes.append(node)
            continue
        split_node_list = node.text.split(delimiter)
        if len(split_node_list) % 2 == 0:
            raise ValueError(f"Invalid Markdown. Symbol ('{delimiter}') not closed")
        for i in range (len(split_node_list)):
            if split_node_list[i] == "":
                continue
            elif i % 2 == 0:
                new_nodes.append(TextNode(split_node_list[i], TextType.PLAIN_TEXT))
            else:
                new_nodes.append(TextNode(split_node_list[i], text_type))

    return new_nodes


def split_nodes_image(nodes):
    new_nodes = []

    for node in nodes:
        image_data = extract_markdown_images(node.text)
        the_text = node.text

        if len(image_data) == 0:
            new_nodes.append(node)
            continue

        for i in range(len(image_data)):
            img_text = image_data[i][0]
            img_url = image_data[i][1]
            the_text = the_text.split(f"![{img_text}]({img_url})", maxsplit=1)
            if len(the_text) != 2:
                raise ValueError("Invalid markdown; image tag not closed")
            if the_text[0] != "":
                new_nodes.append(TextNode(the_text[0], TextType.PLAIN_TEXT))
            new_nodes.append(TextNode(img_text, TextType.IMAGE, img_url))
            the_text = the_text[1]

        if the_text != "":
            new_nodes.append(TextNode(the_text, TextType.PLAIN_TEXT))

    return new_nodes

def split_nodes_link(nodes):
    new_nodes = []

    for node in nodes:
        link_data = extract_markdown_links(node.text)
        the_text = node.text

        if len(link_data) == 0:
            new_nodes.append(node)
            continue

        for i in range(len(link_data)):
            link_text = link_data[i][0]
            link_url = link_data[i][1]
            the_text = the_text.split(f"[{link_text}]({link_url})", maxsplit=1)
            if len(the_text) != 2:
                raise ValueError("Invalid markdown; link tag not closed")
            if the_text[0] != "":
                new_nodes.append(TextNode(the_text[0], TextType.PLAIN_TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            the_text = the_text[1]

        if the_text != "":
            new_nodes.append(TextNode(the_text, TextType.PLAIN_TEXT))

    return new_nodes

# Helper functions; extract Markdown to tuples containing Image and URL data
# provides lists of tuples, e.g. [("image", "google.com")]

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


