import os
import shutil
import sys

from copystatic import copy_files_recursive
from generate import generate_pages_recursive

STATIC_DIR = "static"
OUTPUT_DIR = "docs"
CONTENT_DIR = "content"
TEMPLATE_PATH = "template.html"


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    print(f"Deleting {OUTPUT_DIR} directory...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    print(f"Copying static files from {STATIC_DIR} to {OUTPUT_DIR}...")
    copy_files_recursive(STATIC_DIR, OUTPUT_DIR)
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, OUTPUT_DIR, basepath)


main()
