import re

from blocktype import BlockType
from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType


def text_node_to_html_node(text_node):
    # no match/case in Python < 3.10 :(
    if text_node.text_type is TextType.TEXT:
        return LeafNode(tag = None, value = text_node.text)
    if text_node.text_type is TextType.BOLD:
        return LeafNode(tag = "b", value = text_node.text)
    if text_node.text_type is TextType.ITALIC:
        return LeafNode(tag = "i", value = text_node.text)
    if text_node.text_type is TextType.CODE:
        return LeafNode(tag = "code", value = text_node.text)
    if text_node.text_type is TextType.LINK:
        return LeafNode(tag = "a", value = text_node.text, props = {"href": text_node.url})
    if text_node.text_type is TextType.IMAGE:
        return LeafNode(tag = "img", value = "", props = {
            "src": text_node.url,
            "alt": text_node.text
        })
    raise Exception(f"Unknown text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
        else:
            parts = old_node.text.split(delimiter)
            inner = False
            for part in parts:
                if len(part) > 0:
                    if inner:
                        new_nodes.append(TextNode(part, text_type))
                    else:
                        new_nodes.append(TextNode(part, TextType.TEXT))
                inner = not inner
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text):
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        images = extract_markdown_images(old_node.text)
        if len(images) == 0:
            new_nodes.append(old_node)
        else:
            text_to_process = old_node.text
            for image in images:
                image_alt = image[0]
                image_link = image[1]
                delimiter = f"![{image_alt}]({image_link})"
                parts = text_to_process.split(delimiter, 1)
                if len(parts[0]) > 0:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
                start_index = len(parts[0]) + len(delimiter)
                text_to_process = text_to_process[start_index:]
            if len(text_to_process) > 0:
                new_nodes.append(TextNode(text_to_process, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        links = extract_markdown_links(old_node.text)
        if len(links) == 0:
            new_nodes.append(old_node)
        else:
            text_to_process = old_node.text
            for link in links:
                link_text = link[0]
                link_url = link[1]
                delimiter = f"[{link_text}]({link_url})"
                parts = text_to_process.split(delimiter, 1)
                if len(parts[0]) > 0:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
                start_index = len(parts[0]) + len(delimiter)
                text_to_process = text_to_process[start_index:]
            if len(text_to_process) > 0:
                new_nodes.append(TextNode(text_to_process, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    new_nodes = [TextNode(text, TextType.TEXT)]
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    return split_nodes_delimiter(new_nodes, "`", TextType.CODE)

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks = list(map(lambda block: block.strip(), blocks))
    return list(filter(lambda block: len(block) > 0, blocks))

def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block) is not None:
        return BlockType.HEADING
    if re.match(r"^```.*```$", block, re.DOTALL) is not None:
        return BlockType.CODE
    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    if is_ordered_list(lines):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def is_ordered_list(lines):
    if len(lines) == 0 or not lines[0].startswith("1. "):
        return False
    for idx, line in enumerate(lines[1:]):
        if not line.startswith(f"{idx + 2}. "):
            return False
    return True

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            block = block.replace("\n", " ")
            text_nodes = text_to_textnodes(block)
            html_nodes = list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes))
            block_nodes.append(ParentNode(tag = "p", children = html_nodes))
        if block_type == BlockType.CODE:
            block = block.replace("```", "").lstrip()
            text_node = TextNode(text = block, text_type = TextType.TEXT)
            html_node = text_node_to_html_node(text_node)
            code = ParentNode(tag = "code", children = [html_node])
            block_nodes.append(ParentNode(tag = "pre", children = [code]))
        if block_type == BlockType.HEADING:
            number_of_hash_marks = get_number_of_hash_marks(block)
            block = block.lstrip("#").lstrip()
            text_nodes = text_to_textnodes(block)
            html_nodes = list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes))
            block_nodes.append(ParentNode(tag = f"h{number_of_hash_marks}", children = html_nodes))
        if block_type == BlockType.QUOTE:
            block = block.replace("> ", "").replace("\n", " ").lstrip().replace("> ", "")
            text_nodes = text_to_textnodes(block)
            html_nodes = list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes))
            block_nodes.append(ParentNode(tag = "blockquote", children = html_nodes))
        if block_type == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            lis = []
            for line in lines:
                line = line.replace("- ", "").strip()
                text_nodes = text_to_textnodes(line)
                html_nodes = list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes))
                lis.append(ParentNode(tag = "li", children = html_nodes))
            block_nodes.append(ParentNode(tag = "ul", children = lis))
        if block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            lis = []
            for line in lines:
                line = re.sub(r"^\d\. ", "", line).strip()
                text_nodes = text_to_textnodes(line)
                html_nodes = list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes))
                lis.append(ParentNode(tag = "li", children = html_nodes))
            block_nodes.append(ParentNode(tag = "ol", children = lis))
    return ParentNode(tag = "div", children = block_nodes)

def get_number_of_hash_marks(txt):
    number_of_hash_marks = 0
    for char in txt:
        if char == "#":
            number_of_hash_marks += 1
        else:
            break
    return number_of_hash_marks