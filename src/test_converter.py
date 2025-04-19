import unittest

from blocktype import BlockType
from converter import extract_markdown_images, extract_markdown_links, split_nodes_delimiter, \
    split_nodes_image, split_nodes_link, text_node_to_html_node, text_to_textnodes, markdown_to_blocks, \
    block_to_block_type, markdown_to_html_node
from textnode import TextNode, TextType


class TestConverter(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")

    def test_italic(self):
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code(self):
        node = TextNode("This is a code node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        node = TextNode("This is a link node", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("This is an image node", TextType.IMAGE, "https://example.com/picture.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {
            "src": "https://example.com/picture.jpg",
            "alt": "This is an image node"
        })

    def test_unknown(self):
        node = TextNode("This is an unknown node", None)
        with self.assertRaises(Exception) as e:
            text_node_to_html_node(node)
        self.assertEqual(str(e.exception), "Unknown text type: None")

    def test_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT)
        ])

    def test_delimiter_inner_at_start(self):
        node = TextNode("`The code block` is at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("The code block", TextType.CODE),
            TextNode(" is at the start", TextType.TEXT)
        ])

    def test_delimiter_inner_at_end(self):
        node = TextNode("At the end there is a `code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("At the end there is a ", TextType.TEXT),
            TextNode("code block", TextType.CODE)
        ])

    def test_delimiter_multiple(self):
        node = TextNode("There is `one``two` and another `code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("There is ", TextType.TEXT),
            TextNode("one", TextType.CODE),
            TextNode("two", TextType.CODE),
            TextNode(" and another ", TextType.TEXT),
            TextNode("code block", TextType.CODE)
        ])

    def test_delimiter_bold(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word", TextType.TEXT)
        ])

    def test_extract_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
        ])

    def test_extract_links(self):
        text = "This is text with a [link](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [
            ("link", "https://www.boot.dev")
        ])

    def test_extract_links_multiple(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev")
        ])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png")
            ],
            new_nodes
        )

    def test_split_images_multiple_nodes(self):
        node1 = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) and some more text",
            TextType.TEXT
        )
        node2 = TextNode(
            "There is no image in this text",
            TextType.TEXT
        )
        node3 = TextNode(
            "![some alt text](some image url) There is an image right at the start",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node1, node2, node3])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(" and some more text", TextType.TEXT),
                TextNode("There is no image in this text", TextType.TEXT),
                TextNode("some alt text", TextType.IMAGE, "some image url"),
                TextNode(" There is an image right at the start", TextType.TEXT)
            ],
            new_nodes
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev")
            ],
            new_nodes
        )

    def test_split_links_multiple_nodes(self):
        node1 = TextNode(
            "This is text with a [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png) and some more text",
            TextType.TEXT
        )
        node2 = TextNode(
            "There is no link in this text",
            TextType.TEXT
        )
        node3 = TextNode(
            "[some link text](some link url) There is a link right at the start",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node1, node2, node3])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
                TextNode(" and some more text", TextType.TEXT),
                TextNode("There is no link in this text", TextType.TEXT),
                TextNode("some link text", TextType.LINK, "some link url"),
                TextNode(" There is a link right at the start", TextType.TEXT)
            ],
            new_nodes
        )
    
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes
        )

    def test_text_to_textnodes_no_formatting(self):
        text = "This is just a simple text"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is just a simple text", TextType.TEXT)
            ],
            nodes
        )

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

    def test_block_to_block_type_heading1(self):
        block = "# This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading2(self):
        block = "## This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading3(self):
        block = "### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading4(self):
        block = "#### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading5(self):
        block = "##### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading6(self):
        block = "###### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading_too_many_hash_marks(self):
        block = "####### This is not a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_single_line_code_block(self):
        block = """```This is a single-line code block```"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_multi_line_code_block(self):
        block = """```
This is a
multi-line
code block
```"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_single_line_quote_block(self):
        block = """> This is a single-line quote block"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.QUOTE, block_type)

    def test_block_to_block_type_multi_line_quote_block(self):
        block = """> This is a
> multi-line
> quote block"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.QUOTE, block_type)

    def test_block_to_block_type_not_a_quote_block(self):
        block = """> This is actually
not
> a quote block"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_single_line_unordered_list(self):
        block = """- This is a single-line unordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.UNORDERED_LIST, block_type)

    def test_block_to_block_type_multi_line_unordered_list(self):
        block = """- This is a
- multi-line
- quote block"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.UNORDERED_LIST, block_type)

    def test_block_to_block_type_not_an_unordered_list(self):
        block = """- This is actually
-not
- an unordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_single_line_ordered_list(self):
        block = """1. This is a single-line ordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.ORDERED_LIST, block_type)

    def test_block_to_block_type_multi_line_ordered_list(self):
        block = """1. This is a
2. multi-line
3. ordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.ORDERED_LIST, block_type)

    def test_block_to_block_type_not_ordered_list_does_not_start_with_one(self):
        block = """2. This is not a
3. multi-line
4. ordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_not_ordered_list_does_not_increment_by_one(self):
        block = """1. This is not a
2. multi-line
4. ordered list"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph(self):
        block = """This is
just a
regular paragraph"""
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

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

    def test_heading(self):
        md = "### This is a heading with some **bold** text"

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h3>This is a heading with some <b>bold</b> text</h3></div>",
        )

    def test_quote(self):
        md = """> This is a
> quote
> with some **bold** text"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote with some <b>bold</b> text</blockquote></div>",
        )

    def test_quote_with_empty_line(self):
        md = """> "I am in fact a Hobbit in all but size."
>
> -- J.R.R. Tolkien"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>\"I am in fact a Hobbit in all but size.\" -- J.R.R. Tolkien</blockquote></div>"
        )

    def test_unordered_list(self):
        md = """- This is an
- unordered list
- with some **bold** text"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is an</li><li>unordered list</li><li>with some <b>bold</b> text</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """1. This is an
2. ordered list
3. with some **bold** text"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>This is an</li><li>ordered list</li><li>with some <b>bold</b> text</li></ol></div>",
        )
        

if __name__ == "__main__":
    unittest.main()