import re
import sys
import logging
import logging.config

from vFense.db.client import db_create_close, r, db_connect
from vFense.errorz.error_messages import GenericResults, PackageResults
from vFense.plugins.cve import *
from vFense.plugins.cve.cve_constants import *
from vFense.plugins.cve.search._db import get_ubu_vulnerability_data_by_vuln_id, \
    get_win_vulnerability_data_by_vuln_id

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

class RetrieveByVulnerabilityId(object):
    def __init__(
        self, username, customer_name, vuln_id,
        uri=None, method=None, count=30, offset=0
        ):

        self.vuln_id = vuln_id
        self.username = username
        self.customer_name = customer_name
        self.uri = uri
        self.method = method
        self.count = count
        self.offset = offset
        self.__os_director()

    def __os_director(self):
        if re.search('^MS', self.vuln_id, re.IGNORECASE):
            self.Collection = WindowsSecurityBulletinCollection
            self.Keys = WindowsSecurityBulletinKey
            self.get_vuln_by_id = get_win_vulnerability_data_by_vuln_id

        elif re.search('^USN-', self.vuln_id, re.IGNORECASE):
            self.Collection = UbuntuSecurityBulletinCollection
            self.Keys = UbuntuSecurityBulletinKey
            self.get_vuln_by_id = get_ubu_vulnerability_data_by_vuln_id

    def get_vuln(self):
        data = self.get_vuln_by_id(self.vuln_id)
        if data:
            status = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(data, 1)
            )

        else:
            status = (
                GenericResults(
                    self.username, self.uri, self.method
                ).invalid_id(self.vuln_id, 'vulnerability id')
            )

        return(status)
