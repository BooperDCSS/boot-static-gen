import re
from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, TextNode

# convert full markdown document to single parent HTMLNode with children

def markdown_to_html_node(markdown: str) -> ParentNode:
    all_children = []

    md_blocks = markdown_to_blocks(markdown)
    for block in md_blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            all_children.append(ParentNode(
                f"h{header_counter(block)}", header_to_children(block)
            ))
        elif block_type == BlockType.PARAGRAPH:
            all_children.append(ParentNode(
               "p", para_to_children(block)
            ))
        elif block_type == BlockType.QUOTE:
            all_children.append(ParentNode(
                "blockquote", quote_to_children(block)
            ))
        elif block_type == BlockType.UNORD_LIST:
            all_children.append(ParentNode(
                "ul", render_li_nodes(block)
            ))
        elif block_type == BlockType.ORD_LIST:
            all_children.append(ParentNode(
                "ol", render_li_nodes(block)
            ))
        elif block_type == BlockType.CODE:
            all_children.append(ParentNode(
                "pre", render_codeblock_text(block)
            ))
        else:
            raise ValueError("Block does not match existing block types")

    return ParentNode("div", all_children)

# better separation of responsibility with this version
# simply receives text and converts it, first to a text node, then to HTML node
# returns a list of HTML nodes
def new_text_to_children(text: str) -> list[HTMLNode]:
    child_list = []
    nodes = text_to_textnodes(text)
    for node in nodes:
        child_list.append(text_node_to_html_node(node))
    return child_list

# this contains a cleaner # strip than my previous version
# and it utilizes my helper function to decide where content begins
def header_to_children(block: str) -> list[HTMLNode]:
    h_count = header_counter(block)
    child_text = block[h_count + 1 :]
    if not child_text:
        raise ValueError(f"Invalid header depth: {h_count}")
    return new_text_to_children(child_text)

# fixes problem I had with previous version, which would ignore multi-line
# quotes; also introduces guard for improperlyh formatted quotes
def quote_to_children(text: str) -> list[HTMLNode]:
    quote_lines = text.split("\n")
    clean_quotes = []
    for line in quote_lines:
        if not line.startswith(">"):
            raise ValueError("Missing `>` character: invalid quote block")
        clean_quotes.append(line.lstrip(">").lstrip())
    joined_quote = " ".join(clean_quotes)
    return new_text_to_children(joined_quote)

def para_to_children(text: str) -> list[HTMLNode]:
    clean_para = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == "":
            continue
        clean_para.append(stripped)
    joined_para = " ".join(clean_para)
    return new_text_to_children(joined_para)

def render_li_nodes(text: str) -> list[HTMLNode]:
    li_list = []

    if text.startswith("- "):
        li_split = re.split(r"^- ", text, flags=re.MULTILINE)
    elif text.startswith("1. "):
        li_split = re.split(r"^\d+\. ", text, flags=re.MULTILINE)
    else:
        raise ValueError("List node begins with invalid character")
    for entry in li_split:
        if not entry.strip():
            continue
        entry = entry.rstrip("\n")
        li_list.append(ParentNode("li", new_text_to_children(entry)))

    return li_list

# handle codeblock text by skipping the markdown conversion
# text splicing to avoid issues with lsplit("`\n"), which could get rid of
# opening code text inside the code block... same reason we did that in the
# header code refactor
def render_codeblock_text(text: str) -> LeafNode:
    text = text[3:-3]
    text = text.lstrip("\n")
    code_leaf = text_node_to_html_node(TextNode(text, TextType.CODE_TEXT))
    return [code_leaf]
    
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
