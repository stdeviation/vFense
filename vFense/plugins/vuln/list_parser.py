from bs4 import BeautifulSoup
import requests
import os
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from datetime import datetime

from vFense.utils.common import decoder
from vFense.plugins.vuln._constants import (
    Archives
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class ListParser(object):
    def __init__(self, base_url=None, html_dir=None):
        self.base_url = base_url
        self.html_dir = html_dir

    def vulnerability_id(self):
        pass

    def date_posted(self):
        pass

    def support_url(self):
        pass

    def date(self):
        pass

    def details(self):
        pass

    def apps(self):
        pass

    def vuln_data(self):
        pass

    def get_threads(self):
        """Parse the List and return the list of threads.
            example..
            URL: "https://www.redhat.com/archives/rhsa-announce/"

        Basic Usage:
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.get_threads()
            >>> print threads[0]
            >>> 'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'

        Returns:
            List of urls
            >>> [
                'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
            ]

        """

        threads=[]
        req = requests.get(self.base_url, verify=False)
        soup = BeautifulSoup(req.text)
        threads = (
            map(
                lambda x: os.path.join(self.base_url, x.get("href")),
                soup.findAll(
                    "a", text=re.compile("Thread")
                )
            )
        )

        return threads

    def get_msg_links_by_thread(self, thread):
        """Parse the thread link and return the list of message links.
        Args:
            thread (str) : This should be valid thread url.

        Basic Usage:
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.get_threads()
            >>> print threads[0]
            >>> 'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])

        Returns:
            List of urls
            >>> [
                'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'
            ]
        """

        dlinks = []
        req = requests.get(thread, verify=False)
        if req.ok:
            date = thread.split('/')[-2]
            tsoup=BeautifulSoup(req.text)
            dlinks = (
                map(
                    lambda x: os.path.join(self.base_url, date, x.get('href')),
                    tsoup.find_all(
                        "a", attrs={"href": re.compile("[0-9]+.html")}
                    )
                )
            )

        return dlinks

    def get_html_content(self, hlink, force=False):
        """
        Parse the content of the Message link and return the html content.
        Args:
            hlink (url) : Message link
                example.. https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html

        Basic Usage :
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.get_threads()
            >>> print threads[0]
            >>> 'https://lists.ubuntu.com/archives/ubuntu-security-announce/2015-June/thread.html'
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> parser.get_html_content(msg_links[0])

        Returns:
            html webpage content

        """
        content = None
        date_folder = hlink.split('/')[-2]
        self.make_html_folder(date_folder)

        msg_location = (
            os.path.join(
                self.html_dir, '/'.join(hlink.split('/')[-2:])
            )
        )

        if os.path.exists(msg_location) and not force:
            if os.stat(msg_location).st_size == 0:
                request = requests.get(hlink, verify=False)
                if request.ok:
                    content = request.content
                    msg_file = open(msg_location, 'wb')
                    msg_file.write(content)
                    msg_file.close()
            else:
                content = open(msg_location, 'rb').read()
        else:
            request = requests.get(hlink, verify=False)
            if request.ok:
                content = request.content
                msg_file = open(msg_location, 'wb')
                msg_file.write(content)
                msg_file.close()

        return content

    def make_html_folder(self, dir_name):
        """
        Verify or create the folder to store the html files and return the
        PATH name.

        Args:
            dir_name (str): The folder name.
                example.. 2015-July

        Basic Usage:

            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> parser.make_html_folder('2015-July')

        Returns:
            String
            >>> '/opt/vFense/plugins/vuln/ubuntu/data/html/2015-July/'
        """

        fpath = os.path.join(self.html_dir, dir_name)
        if not os.path.exists(fpath):
            os.makedirs(fpath)

        return fpath

    def cves(self, content):
        """
        Parse cve_ids from the data file and return the list of cve_ids.

        Args:
            content (str): the html content this function will parse.

        Basic Usage:
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.get_threads()
            >>> print threads[0]
            >>> 'https://lists.ubuntu.com/archives/ubuntu-security-announce/2015-June/thread.html'
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> content = parser.get_html_content(msg_links[0])
            >>> parser.cves(content)

        RETURNS:
            List of CVE-IDs for specific redhat vulnerability update.
            [
                'CVE-2010-0174', 'CVE-2010-0175',
                'CVE-2010-0176', 'CVE-2010-0177'
            ]
        """
        cve_ids = list(set(re.findall(r"(CVE-[0-9]+-[0-9]+)", content)))
        return cve_ids

def get_rh_data(content):
    """
    Parse data file to get the vulnerability update Summary, Decsriptions etc. and return
    dictionary data with all the redhay update info.

    Args:
        dfile : data file to parse the cve-ids for specific redhat vulnerabilty updates.

    Basic Usage:
        >>> import os
        >>> os.getcwd()
        '/opt/TopPatch/tp/src/plugins/vuln/redhat'
        >>> from vFense.plugins.vuln.redhat.parser import *
        >>> rh_data=get_rh_data(dfile=dfile)

    RETURNS:
        A dictionary data contents redhat update info.

    """
    redhat = Redhat()
    description_search  = (
        re.search('(Problem description|Description):\n\n(\w.*)\n\n.*\s+Solution', content, re.DOTALL)
    )
    if description_search:
        redhat.details = decoder(description_search.group(2))

    redhat.apps = get_apps_info(content)

    vulnerability_id_search = re.search(r'Advisory\sID:.*', content)
    if vulnerability_id_search:
        redhat.vulnerability_id = (
            vulnerability_id_search.group().split(':', 1)[1].strip()
        )

    advisory_url_search = re.search(r"Advisory\sURL:\s.*", content)
    if advisory_url_search:
        redhat.support_url = (
            BeautifulSoup(advisory_url_search.group()).find('a').text
        )

    date_posted_search = re.search(r"Issue\sdate:\s.*", content)
    if date_posted_search:
        issue_date = date_posted_search.group().split(':',1)[1].strip()
        redhat.date_posted = (
            int(datetime.strptime(issue_date, "%Y-%m-%d").strftime('%s'))
        )

    redhat.cve_ids = get_rh_cve_ids(content)

    return(redhat)

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
