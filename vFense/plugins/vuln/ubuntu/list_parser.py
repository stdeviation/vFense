from bs4 import BeautifulSoup
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from datetime import datetime
from time import mktime

from vFense.utils.common import decoder, month_to_num_month
from vFense.plugins.patching.utils import build_app_id
from vFense.plugins.vuln.list_parser import ListParser
from vFense.plugins.vuln.ubuntu._constants import (
    Archives, UbuntuDataDir
)
from vFense.plugins.vuln.ubuntu import Ubuntu, UbuntuVulnApp
from vFense.plugins.vuln.ubuntu._db import insert_bulletin_data

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class UbuntuListParser(ListParser):
    def __init__(self, **kwargs):
        super(UbuntuListParser, self).__init__(**kwargs)
        self.os_string = 'Ubuntu'
        self.base_url = Archives.ubuntu
        self.html_dir = UbuntuDataDir.HTML_DIR

    def vulnerability_id(self, content):
        """Parse message and retrieve the USN identifier
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import ListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.usn(msg_links[0])

        Returns:
            String
            >>> USN-2626-1
        """
        usn = None
        match = (
            re.search(r'={2,}\s?\n(.*)\n={2,}\n', content, re.MULTILINE|re.DOTALL)
        )

        if match:
            usn_match = (
                re.search(r"USN-[0-9]+-[0-9]+", match.group(1), re.IGNORECASE)
            )
            if usn_match:
                usn = usn_match.group()

        return usn

    def support_url(self, content):
        """Parse message and retrieve the support url
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import ListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.support_url(msg_links[0])

        Returns:
            String
            >>> u'http://www.ubuntu.com/usn/usn-2659-1'
        """
        support_url = None
        soup = BeautifulSoup(content)
        support_url_found = (
            soup.find("a", href = re.compile(r'.*usn-[0-9]+-[0-9]+'))
        )
        if support_url_found:
            support_url = support_url_found.text

        return support_url

    def date_posted(self, content):
        """Parse message and retrieve date in epoch time.
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.date(msg_links[0])

        Returns:
            Float
            >>> 1436241600.0
        """
        date_posted = None
        date_found = (
            re.search(r'={10,}\n(.*)^={10,}\n', content, re.MULTILINE|re.DOTALL)
        )
        if date_found:
            unformatted_date = (
                re.findall(r'\w+ \d+, \d+', date_found.group(1))
            )
            month, day, year = unformatted_date[0].split()
            day = int(day.replace(',',''))
            month = month_to_num_month[month]
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
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.details(msg_links[0])

        RETURNS:
            String
            >>>
        """
        new_pattern = (
            re.compile(r"Details:\n+(.*)\n{2}Update instructions:",
                re.MULTILINE|re.IGNORECASE|re.DOTALL
            )
        )
        old_pattern = (
            re.compile(
                r"Details follow:\n+(.*)\n{3}Update[A-Za-z0-9 .]+:\n",
                re.MULTILINE|re.IGNORECASE|re.DOTALL
            )
        )
        if new_pattern.search(content):
            detail_text = new_pattern.search(content).group(1)
        elif old_pattern.search(content):
            detail_text = old_pattern.search(content).group(1)
        else:
            detail_text = None

        return decoder(detail_text)

    def apps(self, content):
        """
        Parse the list of ubuntu packages from the message and return a list
            of dicts.
        Args:
            content (str): the message content this function will parse.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.apps(msg_links[0])

        RETURNS:
            Tuple (list of strings, list of dicts)
            >>>
            (
                [
                    "Ubuntu 12.04 LTS",
                    "Ubuntu 14.04 LTS"
                ],
                [
                    {
                        "version": "3.2.0-87.125",
                        "app_id": "0c824466dad299aee041f919ed4836117ccef8824440d04c4f4ffcc44c33b4ec",
                        "name": "linux-image-3.2.0-87-powerpc64-smp",
                        "os_string": "Ubuntu 12.04 LTS"
                    },
                    {
                        "version": "3.2.0-87.125",
                        "app_id": "f2ae352a1fd761c501352787dcc1d658ac79e0d2542643a0c848fe5d93a3e634",
                        "name": "linux-image-3.2.0-87-virtual",
                        "os_string": "Ubuntu 12.04 LTS"
                    }
                ]
            )
        """
        app_info = []
        os_strings = []
        match_group = None
        updated_match = (
            re.compile(
                r'(package versions:.*)References:',
                re.MULTILINE|re.IGNORECASE|re.DOTALL)
        )
        old_match = (
            re.compile(
                r'(package versions:.*)Details follow:',
                re.MULTILINE|re.IGNORECASE|re.DOTALL)
        )
        if updated_match.search(content):
            match_group = updated_match.search(content).group(1)
        elif old_match.search(content):
            match_group = old_match.search(content).group(1)

        if match_group:
            for line in match_group.split('\n'):
                os_match = re.search(r'(^Ubuntu.*):', line, re.IGNORECASE)
                if os_match:
                    os_string = os_match.group(1)
                    os_strings.append(os_string)

                elif len(line.split()) == 2 and not re.search(":$", line):
                    app = UbuntuVulnApp()
                    app.fill_in_defaults()
                    app.os_string = os_string
                    app.name, app.version = line.split()
                    app.app_id = build_app_id(app.name, app.version)
                    app_info.append(app.to_dict())

        return(os_strings, app_info)

    def vuln_data(self, content):
        """
        Parse data file to get the vulnerability details and return
        dictionary data with all the update info.

        Args:
            dfile : data file to parse the cve-ids for specific redhat vulnerabilty updates.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> vuln = parser.vuln_data(msg_links[0])


        RETURNS:
            A dictionary data contents redhat update info.
        """
        vuln = Ubuntu()
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


def ubuntu_archive_processor(only_updates=True):
    """
    This will call the function to insert the data into db for all the threads
    and will insert the data one by one.

    Kwargs:
        only_updates (bool): Only process updates that have yet to be
            downloaded to disk. Default=True

    Basic Usage:
        >>> from vFense.plugins.vuln.ubuntu.list_parser import ubuntu_archive_processor
        >>> count = ubuntu_archive_processor(only_updates=False)

    Returns:

    """
    count = 0
    parser = UbuntuListParser()
    vulnerabilities = parser.archives(only_updates, db_ready=True)
    if vulnerabilities:
        count = parser.update(vulnerabilities)
        if count == 0:
            msg = 'There aren\'t any vulnerabilities available'
            logger.info(msg)
            print msg
        else:
            msg = (
                'Ubuntu vulnerabilities updated: {0}'.format(count)
            )
            logger.info(msg)
            logger.info('finished ubuntu usn update process')
            print msg
    return count
