import os
import sys

""" This convention roots the project in the directory that hosts src/config.py...
The idea is to ensure an absolute path no matter where the main.sh or main.py
is run; so this would work from the root of the project as well as from 
anywhere else on the system. Ensures greater security for filepaths. """

CONFIG_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ROOT_DIRECTORY = os.path.dirname(CONFIG_DIRECTORY)
DOCS_DIRECTORY = os.path.join(ROOT_DIRECTORY, "docs")
PUBLIC_DIRECTORY = os.path.join(ROOT_DIRECTORY, "public")
STATIC_DIRECTORY = os.path.join(ROOT_DIRECTORY, "static")
CONTENT_DIRECTORY = os.path.join(ROOT_DIRECTORY, "content")
TEMPLATE_FILE = os.path.join(ROOT_DIRECTORY, "template.html")
