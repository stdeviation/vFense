import os
import vFense.plugins.vuln._constants

class Archives(vFense.plugins.vuln._constants.Archives):
    redhat = 'https://www.redhat.com/archives/rhsa-announce'

REDHAT = 'redhat'
REDHAT_ARCHIVE = 'https://www.redhat.com/archives/rhsa-announce'

class RedhatDataDir():
    PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))
    HTML_DIR = os.path.join(PLUGIN_DIR, 'data/html/')

class RedhatVulnSubKeys():
    NAME = 'name'
    VERSION = 'version'
    ARCH = 'arch'
    APP_ID = 'app_id'
    OS_STRING = 'os_string'
