import os

ROOT_DIRECTORY = os.path.abspath(os.getcwd())
PUBLIC_DIRECTORY = os.path.normpath(os.path.join(ROOT_DIRECTORY, "public/"))
STATIC_DIRECTORY = os.path.normpath(os.path.join(ROOT_DIRECTORY, "static/"))
