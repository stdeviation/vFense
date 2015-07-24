from bs4 import BeautifulSoup
import requests
import os
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class ListParser(object):
    def __init__(self, os_string=None, base_url=None, html_dir=None,
                 verbose=False):
        self.os_string = os_string
        self.base_url = base_url
        self.html_dir = html_dir
        self.verbose = verbose

    def vulnerability_id(self):
        pass

    def date_posted(self):
        pass

    def support_url(self):
        pass

    def month_year(self, thread):
        parsed_date = thread.split('/')[-2]
        return parsed_date

    def details(self):
        pass

    def apps(self):
        pass

    def vuln_data(self):
        pass

    def update(self):
        pass

    def threads(self):
        """Parse the List and return the list of threads.
            example..
            URL: "https://www.redhat.com/archives/rhsa-announce/"

        Basic Usage:
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.threads()
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
            >>> threads = parser.threads()
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
            soup = BeautifulSoup(req.text)
            dlinks = (
                map(
                    lambda x: os.path.join(self.base_url, date, x.get('href')),
                    soup.find_all(
                        "a", attrs={"href": re.compile("[0-9]+.html")}
                    )
                )
            )

        return dlinks

    def get_html_content(self, hlink, force=False, only_updates=False):
        """
        Parse the content of the Message link and return the html content.
        Args:
            hlink (url) : Message link
                example.. https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html
            force (bool): Retrieve message from the archive and not from disk,
                if the archive is already on disk.
            only_updates (bool): Retrieve message only if it isn't on disk.

        Basic Usage :
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.threads()
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

        if os.path.exists(msg_location) and not force and not only_updates:
            if os.stat(msg_location).st_size == 0:
                request = requests.get(hlink, verify=False)
                if request.ok:
                    content = request.content
                    msg_file = open(msg_location, 'wb')
                    msg_file.write(content)
                    msg_file.close()
            else:
                content = open(msg_location, 'rb').read()

        elif (not os.path.exists(msg_location) or
              os.path.exists(msg_location) and force or
              not os.path.exists(msg_location) and only_updates):
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
            >>> threads = parser.threads()
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

    def archives(self, only_updates=True, db_ready=False):
        """
        This method will retrieve and parse all the threads in the selected
        archive and return them in a list of dicts. The data returned,
        is ready to be inserted into the database.

        Kwargs:
            only_updates (bool): If set to False, this will retrieve all
                archives from disk and from the web archives.
                default=True This will fetch archives from the web, that do
                not exist on disk.
            db_ready (bool): Return the data in which the database can
                understand (List of Dictionaries instead of a List
                of Vulnerability Objects. Default=False

        Basic Usage:
            >>> from vFense.plugins.vuln.list_parser import ListParser
            >>> parser = ListParser('https://lists.ubuntu.com/archives/ubuntu-security-announce')
            >>> threads = parser.threads()
            >>> print threads[0]
            >>> 'https://lists.ubuntu.com/archives/ubuntu-security-announce/2015-June/thread.html'
            >>> msg_links = parser.get_msg_links_by_thread(threads[0])
            >>> content = parser.get_html_content(msg_links[0])
            >>> parser.cves(content)

        RETURNS:
            List of formatted updates
            [
            ]
        """
        vulnerabilities = []
        threads = self.threads()
        for thread in threads:
            if self.verbose:
                msg = (
                    "Processing {0} vulnerabilties for {1}"
                    .format(self.os_string, self.month_year(thread))
                )
                print msg
                logger.debug(msg)

            messages = self.get_msg_links_by_thread(thread)
            for message in messages:
                content = self.get_html_content(
                    message, only_updates=only_updates
                )
                if content:
                    if (self.vulnerability_id(content) and
                            self.date_posted(content)):
                        vuln = self.vuln_data(content)
                        if db_ready:
                            vulnerabilities.append(vuln.to_dict_db())
                        else:
                            vulnerabilities.append(vuln)
                else:
                    break

        return vulnerabilities
