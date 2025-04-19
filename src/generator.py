import os
from converter import markdown_to_html_node

TITLE_PLACEHOLDER = "{{ Title }}"
CONTENT_PLACEHOLDER = "{{ Content }}"

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line.replace("# ", "", 1).strip()
    raise Exception("Markdown has no title")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    from_file = open(from_path)
    markdown = from_file.read()
    template_file = open(template_path)
    template = template_file.read()
    
    title = extract_title(markdown)
    html_node = markdown_to_html_node(markdown)
    content = html_node.to_html()
    html = template.replace(TITLE_PLACEHOLDER, title).replace(CONTENT_PLACEHOLDER, content)
    
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok = True)
    dest_file = open(dest_path, 'w')
    dest_file.write(html)

    dest_file.close()
    template_file.close()
    from_file.close()

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    children = os.listdir(dir_path_content)
    for child in children:
        path = os.path.join(dir_path_content, child)
        path_without_root = path.split(os.path.sep, 1)[1]
        destination = os.path.join(dest_dir_path, path_without_root)
        if os.path.isfile(path):
            generate_page(path, template_path, destination.replace(".md", ".html"))
        else:
            generate_pages_recursive(path, template_path, dest_dir_path)