import os
import sys


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS  # type: ignore
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
