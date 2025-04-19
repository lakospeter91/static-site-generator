import os
import shutil
import sys
from generator import generate_pages_recursive

CONTENT = "content"
DOCS = "docs"
STATIC = "static"
TEMPLATE = "template.html"

def main():
    base_path = "/"
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    print(f"Base path: {base_path}")
    if os.path.exists(STATIC):
        print(f"Copying assets from directory '{STATIC}' to directory '{DOCS}'")
        if os.path.exists(DOCS):
            print(f"Removing directory '{DOCS}'")
            shutil.rmtree(DOCS)
        print(f"Creating directory '{DOCS}'")
        os.mkdir(DOCS)
        copy(STATIC, DOCS)
    else:
        print(f"Directory '{STATIC}' does not exist")
    generate_pages_recursive(CONTENT, TEMPLATE, DOCS, base_path)

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
            copy(path, DOCS)

main()
