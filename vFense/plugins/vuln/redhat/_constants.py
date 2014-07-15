import os

REDHAT = 'redhat'
REDHAT_ARCHIVE = 'https://www.redhat.com/archives/rhsa-announce/'

class RedhatDataDir():
    PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))
    HTML_DIR = os.path.join(PLUGIN_DIR, 'data/html/')
