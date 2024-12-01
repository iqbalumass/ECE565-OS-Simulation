import os

'''
To access paths.py from a file inside another folder use the following:

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import *

else:
from paths import*


'''


# Define the project root (relative to the location of this file)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define dynamic paths for different parts of your project
STORAGE_DIR = os.path.join(PROJECT_ROOT, 'Storage')
PROCESS_DIR = os.path.join(PROJECT_ROOT, 'Process')

# Example paths within the Storage directory
INDEXED_DIR = os.path.join(STORAGE_DIR, 'indexed')
CONTIGUOUS_DIR = os.path.join(STORAGE_DIR, 'contiguous')
LINKED_DIR = os.path.join(STORAGE_DIR, 'linked')

BLOCK_ENTRIES_PATH = os.path.join(INDEXED_DIR, 'block_entries.json')
DIRECTORY_PATH = os.path.join(INDEXED_DIR, 'directory.json')

# Add more paths as needed
