import os
import shutil

from copystatic import copy_files_recursive

STATIC_DIR = "static"
PUBLIC_DIR = "public"


def main():
    print(f"Deleting {PUBLIC_DIR} directory...")
    if os.path.exists(PUBLIC_DIR):
        shutil.rmtree(PUBLIC_DIR)
    print(f"Copying static files from {STATIC_DIR} to {PUBLIC_DIR}...")
    copy_files_recursive(STATIC_DIR, PUBLIC_DIR)


main()
