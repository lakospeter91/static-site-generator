import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_to_html(self):
        html_node = HTMLNode(tag = "b", value = "Hello World")
        with self.assertRaises(NotImplementedError):
            html_node.to_html()

    def test_props_to_html_none(self):
        html_node = HTMLNode()
        html = html_node.props_to_html()
        self.assertEqual(html, "")

    def test_props_to_html(self):
        html_node = HTMLNode(tag = "img", props = {"src": "https://www.example.com/picture.jpg"})
        html = html_node.props_to_html()
        self.assertEqual(html, " src=\"https://www.example.com/picture.jpg\"")

    def test_props_to_html_multiple(self):
        html_node = HTMLNode(tag = "a", value = "Google it!", props = {
            "href": "https://www.google.com",
            "target": "_blank"
        })
        html = html_node.props_to_html()
        self.assertEqual(html, " href=\"https://www.google.com\" target=\"_blank\"")

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), "<a href=\"https://www.google.com\">Click me!</a>")

    def test_leaf_to_html_raw(self):
        node = LeafNode(None, "Hello World")
        self.assertEqual(node.to_html(), "Hello World")

    def test_leaf_to_html_none_value(self):
        node = LeafNode(None, None)
        with self.assertRaises(ValueError) as v:
            node.to_html()
        self.assertEqual(str(v.exception), "All leaf nodes must have a value.")

class TestParentNode(unittest.TestCase):
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

    def test_to_html_uneven_depth(self):
        leaf_child_node = LeafNode("b", "child")
        grandchild_node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node, leaf_child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><a href=\"https://www.google.com\">Click me!</a></span><b>child</b></div>",
        )

    def test_to_html_no_children(self):
        node = ParentNode("a", None)
        with self.assertRaises(ValueError) as v:
            node.to_html()
        self.assertEqual(str(v.exception), "All parent nodes must have children.")

if __name__ == "__main__":
    unittest.main()