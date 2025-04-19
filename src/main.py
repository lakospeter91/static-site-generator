import os
import shutil
from generator import generate_pages_recursive
from textnode import TextNode, TextType

CONTENT = "content"
PUBLIC = "public"
STATIC = "static"
TEMPLATE = "template.html"

def main():
    if os.path.exists(STATIC):
        print(f"Copying assets from directory '{STATIC}' to directory '{PUBLIC}'")
        if os.path.exists(PUBLIC):
            print(f"Removing directory '{PUBLIC}'")
            shutil.rmtree(PUBLIC)
        print(f"Creating directory '{PUBLIC}'")
        os.mkdir(PUBLIC)
        copy(STATIC, PUBLIC)
    else:
        print(f"Directory '{STATIC}' does not exist")
    generate_pages_recursive(CONTENT, TEMPLATE, PUBLIC)

def copy(dir, destination_root):
    children = os.listdir(dir)
    for child in children:
        path = os.path.join(dir, child)
        path_without_root = path.split(os.path.sep, 1)[1]
        destination = os.path.join(destination_root, path_without_root)
        if os.path.isfile(path):
            print(f"Copying {path} to {destination}")
            shutil.copy(path, destination)
        else:
            if not os.path.exists(destination):
                print(f"Creating directory '{destination}'")
                os.mkdir(destination)
            copy(path, PUBLIC)

main()
