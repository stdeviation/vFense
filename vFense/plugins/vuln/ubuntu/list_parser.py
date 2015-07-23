from bs4 import BeautifulSoup
import requests
import os
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
from vFense.plugins.patching.utils import build_app_id
from vFense.plugins.vuln.ubuntu import Ubuntu, UbuntuVulnApp
from vFense.plugins.vuln.redhat._db import insert_bulletin_data

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class UbuntuListParser(ListParser):
    def __init__(self):
        self.base_url = Archives.ubuntu
        self.html_dir = UbuntuDataDir.HTML_DIR

    def vulnerability_id(self, content):
        """Parse message and retrieve the USN identifier
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import ListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.get_threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.usn(msg_links[0])

        Returns:
            String
            >>> USN-2626-1
        """
        usn = (
            re.search(
                r'=+\n(.*)^=+\n', content,
                re.MULTILINE|re.DOTALL
            ).group(1).replace('\n\n','\n').split('\n')[0].split()[-1]
        )

        return usn

    def support_url(self, content):
        """Parse message and retrieve the support url
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import ListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.get_threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.support_url(msg_links[0])

        Returns:
            String
            >>> u'http://www.ubuntu.com/usn/usn-2659-1'
        """
        soup = BeautifulSoup(content)
        support_url = (
            soup.find("a", href = re.compile(r'.*usn-[0-9]+-[0-9]+')).text
        )

        return support_url

    def date(self, content):
        """Parse message and retrieve date in epoch time.
        Args:
            content (str): The content of the message we are parsing.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.get_threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.date(msg_links[0])

        Returns:
            Float
            >>> 1436241600.0
        """
        date_posted = u''
        unformatted_date = (
            re.search(
                r'=+\n(.*)^=+\n', content,
                re.MULTILINE|re.DOTALL
            ).group(1).replace('\n\n','\n').split('\n')[1]
        )
        month, day, year = unformatted_date.split()
        day = int(day.replace(',',''))
        month = month_to_num_month[month]
        year = int(year)
        date_posted = mktime(datetime(year, month, day).timetuple())

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
            >>> threads = parser.get_threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.details(msg_links[0])

        RETURNS:
            String
            >>>
        """
        detail_text = (
            re.search(
                r'Details:\n\n(.*)\n\n.*Update instructions:', content,
                re.MULTILINE|re.IGNORECASE|re.DOTALL)
        )
        if detail_text:
            detail_text = decoder(detail_text.group(1))

        return detail_text

    def apps(self, content):
        """
        Parse the list of ubuntu packages from the message and return a list
            of dicts.
        Args:
            content (str): the message content this function will parse.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.get_threads()
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
        app_text = (
            re.search(
                r'(package versions:.*)References:', content,
                re.MULTILINE|re.IGNORECASE|re.DOTALL)
        )
        if app_text:
            for line in app_text.group(1).split('\n'):
                os_match = re.search(r'(^Ubuntu.*):', line, re.IGNORECASE)
                if os_match:
                    os_string = os_match.group(1)
                    os_strings.append(os_string)

                elif len(line.split()) == 2 and not re.search(":", line):
                    app = UbuntuVulnApp()
                    app.fill_in_defaults()
                    app.os_string = os_string
                    app.name, app.version = line.split()
                    app.app_id = build_app_id(app.name, app.version)
                    app_info.append(app.to_dict())

        return(os_strings, app_info)

    def vuln_data(self, content):
        """
        Parse data file to get the vulnerability update Summary, Decsriptions etc. and return
        dictionary data with all the redhay update info.

        Args:
            dfile : data file to parse the cve-ids for specific redhat vulnerabilty updates.

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.list_parser import UbuntuListParser
            >>> parser = UbuntuListParser()
            >>> threads = parser.get_threads()
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> vuln = parser.vuln_data(msg_links[0])


        RETURNS:
            A dictionary data contents redhat update info.
        """
        vuln = Ubuntu()
        vuln.fill_in_defaults()
        vuln.date_posted = self.date(content)
        vuln.vulnerability_id = self.vulnerability_id(content)
        vuln.cve_ids = self.cves(content)
        vuln.os_strings, vuln.apps = self.apps(content)
        vuln.support_url = self.support_url(content)
        vuln.details = self.details(content)
        return vuln

    def insert_data_to_db(thread, latest=False):
        """
        Insert the redhat vulnerability updates parsed from data files to the db. It first collects
        data link parsed from threads and then parse each data link and update the list of updates to
        db for the thread.

        ARGS:
            thread : redhat update thread link for specific month

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.parser import *
            >>> threads = get_threads()
            >>> thread =threads[0]
            >>> insert = insert_data_to_db(thread=thread)

        """
        vulnerabilities = []
        msg_links = get_msg_links_by_thread(thread)
        update_completed = False
        date = None
        if msg_links:
            date = thread.split('/')[-2]
            make_html_folder(date)

            for link in msg_links:
                if latest:
                    content = get_html_latest_content(link)
                    if content:
                        redhat = get_rh_data(content)
                        if redhat.vulnerability_id:
                            vulnerabilities.append(redhat.to_dict_db())
                    else:
                        update_completed = True
                        break
                else:
                    content = get_html_content(link)
                    if content:
                        redhat = get_rh_data(content)
                        if redhat.vulnerability_id:
                            vulnerabilities.append(redhat.to_dict_db())

            _, count, _, _  = insert_bulletin_data(bulletin_data=vulnerabilities)
            return(count, date, update_completed)


def begin_redhat_archive_processing(latest=False):
    """
    This will call the function to insert the data into db for all the threads
    and will insert the data one by one.

    Basic Usage:
        >>> from vFense.plugins.vuln.redhat.parser import *
        >>> update_all_redhat_data()

    """
    threads=get_threads()
    if threads:
        for thread in threads:
            count, date, update_completed = insert_data_to_db(thread, latest)
            if latest and update_completed:
                msg = 'There aren\'t any vulnerabilities available'
                logger.info(msg)
                print msg
                break
            else:
                msg = (
                    'RedHat vulnerabilities inserted: {0} for Year/Month: {1}'
                    .format(count, date)
                )
                logger.info(msg)
                print msg
