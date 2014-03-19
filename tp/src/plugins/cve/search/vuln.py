import re
import sys
import logging
import logging.config
from vFense.db.client import db_create_close, r, db_connect
from vFense.plugins.cve import *
from vFense.plugins.cve.cve_constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')
