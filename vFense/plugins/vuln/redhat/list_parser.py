from bs4 import BeautifulSoup
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from datetime import datetime
from time import mktime

from vFense.utils.common import decoder
from vFense.plugins.patching.utils import build_app_id
from vFense.plugins.vuln.list_parser import ListParser
from vFense.plugins.vuln.redhat._constants import (
    Archives, RedhatDataDir
)
from vFense.plugins.vuln.redhat import Redhat, RedhatVulnApp
from vFense.plugins.vuln.redhat._db import insert_bulletin_data

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class RedhatListParser(ListParser):
    def __init__(self, **kwargs):
        super(RedhatListParser, self).__init__(**kwargs)
        self.os_string = 'Redhat'
        self.base_url = Archives.redhat
        self.html_dir = RedhatDataDir.HTML_DIR

    def vulnerability_id(self, content):
        """Parse message and retrieve the USN identifier
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import ListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.usn(msg_links[0])

        Returns:
            String
            >>> RHSA-2015:1455-01
        """
        rhsa = None
        match = (
            re.search(
                r'Advisory ID:\s+([A-Z]+-[0-9]{4}:[0-9]{4}-[0-9]{1,})\n',
                content
            )
        )

        if match:
            rhsa = match.group(1)

        return rhsa

    def support_url(self, content):
        """Parse message and retrieve the support url
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import ListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.support_url(msg_links[0])

        Returns:
            String
            >>> u'http://www.redhat.com/usn/usn-2659-1'
        """
        soup = BeautifulSoup(content)
        support_url = None
        match = soup.find("a", href=re.compile(r'http*'))

        if match:
            support_url = match.text

        return support_url

    def date_posted(self, content):
        """Parse message and retrieve date in epoch time.
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import RedhatListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.date(msg_links[0])

        Returns:
            Float
            >>> 1436241600.0
        """
        date_posted = None
        date_found = (
            re.search(r'Issue date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})', content)
        )
        if date_found:
            year, month, day = date_found.group(1).split("-")
            day = int(day)
            month = int(month)
            year = int(year)
            date_posted = mktime(datetime(year, month, day).timetuple())

        else:
            if self.verbose:
                print content

        return date_posted

    def details(self, content):
        """
        Return the details of the message, that explains the details of this
            vulnerability
        Args:
            content (str): the message content this function will parse.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import RedhatListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.details(msg_links[0])

        RETURNS:
            String
            >>>
        """
        pattern = (
            re.compile(
                r"[0-9]+\.\s+Description:\n+(.*)\n{2}[0-9]+\.\s+Solution:",
                re.MULTILINE|re.IGNORECASE|re.DOTALL
            )
        )
        if pattern.search(content):
            detail_text = pattern.search(content).group(1)
        else:
            detail_text = None

        return decoder(detail_text)

    def apps(self, content):
        """
        Parse the list of redhat packages from the message and return a list
            of dicts.
        Args:
            content (str): the message content this function will parse.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import RedhatListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.apps(msg_links[0])

        RETURNS:
            Tuple (list of strings, list of dicts)
            >>>
            (
                [
                    "Redhat 12.04 LTS",
                    "Redhat 14.04 LTS"
                ],
                [
                    {
                        "version": "3.2.0-87.125",
                        "app_id": "0c824466dad299aee041f919ed4836117ccef8824440d04c4f4ffcc44c33b4ec",
                        "name": "linux-image-3.2.0-87-powerpc64-smp",
                        "os_string": "Redhat 12.04 LTS"
                    },
                    {
                        "version": "3.2.0-87.125",
                        "app_id": "f2ae352a1fd761c501352787dcc1d658ac79e0d2542643a0c848fe5d93a3e634",
                        "name": "linux-image-3.2.0-87-virtual",
                        "os_string": "Redhat 12.04 LTS"
                    }
                ]
            )
        """
        app_info = []
        os_strings = []
        rpms = set(re.findall(r'([A-Za-z0-9:_.-]+rpm)\n', content))
        print self.vulnerability_id(content)
        for rpm in rpms:
            app = RedhatVulnApp()
            app.fill_in_defaults()
            app.name = re.search(r'(^[A-Za-z0-9-_]+)?-', rpm).group(1)
            if app.name:
                pkg = re.sub(r'(^[A-Za-z0-9-]+)?-', '', rpm)
                app.version = '.'.join(pkg.split('.')[:-2])
                app.arch = pkg.split('.')[-2]
                os_string = re.sub(r'a?el', '', pkg.split('.')[-3])
                app.os_string = (
                    'Red Hat Enterprise Linux {0}'.format(os_string)
                )
                os_strings.append(app.os_string)
                app.app_id = build_app_id(app.name, app.version)
                app_info.append(app.to_dict())

        os_strings = list(set(os_strings))
        return(os_strings, app_info)

    def vuln_data(self, content):
        """
        Parse data file to get the vulnerability details and return
        dictionary data with all the update info.

        Args:
            dfile : data file to parse the cve-ids for specific redhat vulnerabilty updates.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.list_parser import RedhatListParser
            >>> parser = RedhatListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> vuln = parser.vuln_data(msg_links[0])


        RETURNS:
            A dictionary data contents redhat update info.
        """
        vuln = Redhat()
        vuln.fill_in_defaults()
        vuln.date_posted = self.date_posted(content)
        vuln.vulnerability_id = self.vulnerability_id(content)
        vuln.cve_ids = self.cves(content)
        vuln.os_strings, vuln.apps = self.apps(content)
        vuln.support_url = self.support_url(content)
        vuln.details = self.details(content)
        return vuln

    def update(self, vulnerabilities):
        """
        Insert the vulnerability updates parsed from data files to the db.

        ARGS:
            vulnerabilties (list): List of dicts that contain the preformatted
                vulnerability data.

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.parser import *
            >>> threads = threads()
            >>> thread =threads[0]
            >>> insert = insert_data_to_db(thread=thread)

        """
        _, count, _, _  = insert_bulletin_data(bulletin_data=vulnerabilities)
        return count


def redhat_archive_processor(only_updates=True):
    """
    This will call the function to insert the data into db for all the threads
    and will insert the data one by one.

    Kwargs:
        only_updates (bool): Only process updates that have yet to be
            downloaded to disk. Default=True

    Basic Usage:
        >>> from vFense.plugins.vuln.redhat.list_parser import redhat_archive_processor
        >>> count = redhat_archive_processor(only_updates=False)

    Returns:

    """
    count = 0
    parser = RedhatListParser()
    vulnerabilities = parser.archives(only_updates, db_ready=True)
    if vulnerabilities:
        count = parser.update(vulnerabilities)
        if count == 0:
            msg = 'There aren\'t any vulnerabilities available'
            logger.info(msg)
            print msg
        else:
            msg = (
                'Redhat vulnerabilities updated: {0}'.format(count)
            )
            logger.info(msg)
            logger.info('finished Red Hat RHSA update process')
            print msg
    return count
