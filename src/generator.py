import os
import sys
import shutil
import logging
from conversions import markdown_to_html_node, extract_title
from config import PUBLIC_DIRECTORY, STATIC_DIRECTORY, ROOT_DIRECTORY, CONTENT_DIRECTORY
from htmlnode import HTMLNode, LeafNode, ParentNode

logger = logging.getLogger(__name__)

def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    if not os.path.exists(from_path):
        raise Exception("File not found. Check path to ensure file exists.")
    if not os.path.exists(template_path):
        raise Exception("HTML template missing from root directory.")

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    print(f"Generating page from {os.path.relpath(from_path, ROOT_DIRECTORY)} to {os.path.relpath(dest_path, ROOT_DIRECTORY)} using {os.path.relpath(template_path, ROOT_DIRECTORY)}")

    _, ext = os.path.splitext(from_path)
    if ext != ".md":
        raise ValueError(f"Invalid file type: {ext}. This program converts .md files. Stopping conversion.")
    with open(from_path) as md:
        source_md = md.read()
    with open(template_path) as template:
        template_html = template.read()
    html_title = extract_title(source_md)
    html_content = markdown_to_html_node(source_md).to_html()

    new_html = template_html.replace("{{ Content }}", html_content).replace("{{ Title }}", html_title)

    with open(dest_path, 'w', encoding="utf-8") as f:
        f.write(new_html)
        print(f"Success! {os.path.relpath(dest_path)} created")


def generate_pages_recursive(from_path: str, template_path: str, dest_path: str) -> None:
    if not os.path.exists(from_path):
        raise Exception("No content found. Place your .md files inside `ROOT_DIRECTORY/content`.")
    if not os.path.exists(template_path):
        raise Exception("HTML template missing from root directory.")
    
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
        print(f"Created directory at {os.path.relpath(dest_path)}")

    content_dir_list = os.listdir(from_path)
    if len(content_dir_list) < 1:
        raise ValueError("Content directory is empty; add your .md files to the `content` directory.")
    for item in content_dir_list:
        file_path = os.path.join(from_path, item)

        if os.path.isdir(file_path):
            generate_pages_recursive(
                file_path,
                template_path,
                os.path.join(dest_path, item)
            )


        elif os.path.isfile(file_path):
            file_name, ext = os.path.splitext(item)
            target_path = os.path.join(dest_path, file_name + ".html")
            generate_page(file_path, template_path, target_path)


def static_to_public(source: str, target: str) -> None:
    try:
        source_dir_list = os.listdir(source)
        if not os.path.exists(target):
            os.mkdir(target)
            logger.info(f"Directory created: `{os.path.relpath(target, ROOT_DIRECTORY)}`")
    except Exception:
        logger.exception(
            "mkdir operation failed: check source and target variables in src/config.py"
        )
        raise

    try:
        for item in source_dir_list:
            file_path = os.path.join(source, item)
            target_path = os.path.join(target, item)
            if os.path.isfile(file_path):
                shutil.copy(file_path, target)
                logger.info(
                    f"File `{os.path.relpath(file_path, ROOT_DIRECTORY)}` copied to `{os.path.relpath(target, ROOT_DIRECTORY)}`"
                )
            elif os.path.isdir(file_path):
                static_to_public(
                    file_path,
                    target_path,
                )
    except Exception:
        logger.exception(
            "copy operation failed: check source and target variables in src/config.py"
        )
        raise
