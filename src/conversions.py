import re
from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, TextNode

# convert full markdown document to single parent HTMLNode with children

def markdown_to_html_node(markdown: str) -> HTMLNode:
    all_children = []

    md_blocks = markdown_to_blocks(markdown)
    for block in md_blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            all_children.append(ParentNode(
                f"h{header_counter(block)}", text_to_children(block)
            ))
        elif block_type == BlockType.PARAGRAPH:
            all_children.append(ParentNode(
               "p", text_to_children(block)
            ))
        elif block_type == BlockType.QUOTE:
            all_children.append(ParentNode(
                "blockquote", text_to_children(block)
            ))
        elif block_type == BlockType.UNORD_LIST:
            all_children.append(ParentNode(
                "ul", text_to_children(block)
            ))
        elif block_type == BlockType.ORD_LIST:
            all_children.append(ParentNode(
                "ol", text_to_children(block)
            ))
        elif block_type == BlockType.CODE:
            all_children.append(ParentNode(
                "pre", render_codeblock_text(block)
            ))
        else:
            raise ValueError("Block does not match existing block types")

    return ParentNode("div", all_children)


def text_to_children(md: str) -> list[HTMLNode]:
    child_list = []
    if md.startswith("#"):
        child_text = md.lstrip("# ")
        text_node_list = text_to_textnodes(child_text)
        for node in text_node_list:
            child_list.append(text_node_to_html_node(node))
    elif md.startswith(">"):
        child_text = md.lstrip("> ")
        text_node_list = text_to_textnodes(child_text)
        for node in text_node_list:
            child_list.append(text_node_to_html_node(node))
    elif md.startswith("- "):
        child_list.extend(create_li_nodes(md))
    elif md.startswith("1. "):
        child_list.extend(create_li_nodes(md))
    else:
        child_text = md.lstrip().replace("\n", " ").rstrip()
        text_node_list = text_to_textnodes(child_text)
        for node in text_node_list:
            child_list.append(text_node_to_html_node(node))

    return child_list

# handle codeblock text by skipping the markdown conversion
def render_codeblock_text(text: str) -> LeafNode:
    text = text.lstrip("\n```").rstrip("```")
    code_leaf = text_node_to_html_node(TextNode(text, TextType.CODE_TEXT))
    return [code_leaf]
    
# quick way to create <li> Leaf Nodes for <ul> and <ol>
def create_li_nodes(md: str) -> list[LeafNode]:
    li_list = []

    if md.startswith("- "):
        li_split = md.split("- ")
    if md.startswith("1. "):
        li_split = re.split(r"^\d\. ", md, flags=re.MULTILINE)
    for entry in li_split:
        if entry == "\n" or entry == "":
            continue
        entry = entry.rstrip("\n")
        li_list.append(LeafNode("li", entry)) 

    return li_list


# easy way to get the right heading number from number of # in string
def header_counter(block: str) -> int:
    count = 0
    for c in block:
        if c == "#":
            count += 1
        if c == " ":
            return count

# Creating HTML-related inline nodes from TextNodes...

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
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

# Returns block type based on individual blocks of Markdown

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORD_LIST = "unordered list"
    ORD_LIST = "ordered list"

def block_to_block_type(block: str) -> BlockType:
    heading_match = re.match(r"^#{1,6} ", block) # the ^ char checks beginning of string
    lines = block.split("\n")

    if heading_match:
        return BlockType.HEADING
    elif block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    elif block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    elif block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORD_LIST
    elif block.startswith("1. "):
        line_number = 1
        for line in lines:
            if not line.startswith(f"{line_number}. "):
                return BlockType.PARAGRAPH
            line_number += 1
        return BlockType.ORD_LIST
    else:
        return BlockType.PARAGRAPH

# converts full Markdown text to a list of TextNodes using the split_nodes functions

def text_to_textnodes(text: str) -> list[TextNode]:

    original_text = TextNode(text, TextType.PLAIN_TEXT)
    bold_split = split_nodes_delimiter([original_text], "**", TextType.BOLD)
    italic_split = split_nodes_delimiter(bold_split, "_", TextType.ITALIC)
    code_split = split_nodes_delimiter(italic_split, "`", TextType.CODE_TEXT)
    image_split = split_nodes_image(code_split)
    link_split = split_nodes_link(image_split)

    return link_split

# converts multi-line Markdown text to individual "blocks" of strings using \n\n

def markdown_to_blocks(md: str) -> list[str]:
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

def split_nodes_delimiter(nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
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


def split_nodes_image(nodes: list[TextNode]) -> list[TextNode]:
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

def split_nodes_link(nodes: list[TextNode]) -> list[TextNode]:
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

def extract_markdown_images(text: str) -> tuple[str, str]:
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text: str) -> tuple[str, str]:
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches
