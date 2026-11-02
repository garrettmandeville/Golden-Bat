"""
File Path Helpers

Description: Resolves paths to bundled resources (data/ and assets/) for both source
             runs and PyInstaller builds.
"""

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_path(*parts):
    """Returns an absolute path to a bundled resource, e.g. resource_path("data", "rooms.json")."""
    # PyInstaller creates a temporary folder and stores path in _MEIPASS
    base_dir = getattr(sys, '_MEIPASS', PROJECT_ROOT)
    return os.path.join(base_dir, *parts)
