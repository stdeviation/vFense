from bs4 import BeautifulSoup
import requests
import os
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from datetime import datetime


from vFense.utils.common import decoder
from vFense.plugins.patching.utils import build_app_id
from vFense.plugins.vuln.redhat import Redhat, RedhatVulnApp
from vFense.plugins.vuln.redhat._constants import (
    RedhatDataDir, REDHAT_ARCHIVE
)
from vFense.plugins.vuln.redhat._db import insert_bulletin_data

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

URL = REDHAT_ARCHIVE

def get_threads():

    """Parse the Redhat Official Annouces (URL: "https://www.redhat.com/archives/rhsa-announce/")
        and return the list of threads.

    Basic Usage:
        >>> from vFense.plugins.vuln.redhat.parser import get_threads
        >>> threads = get_threads()

    Returns:
        List of urls
        >>> [
            'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
        ]

    """

    threads=[]
    req = requests.get(URL, verify=False)
    soup= BeautifulSoup(req.text)
    threads = (
        map(
            lambda x: os.path.join(URL, x.get("href")),
            soup.findAll(
                "a", text=re.compile("Thread")
            )
        )
    )

    return(threads)

def get_msg_links_by_thread(thread):
    """Parse the Redhat update thread link and return the list of data link or message link.
    Args:
        thread (str) : This should be valid Redhat thread url.

    Basic Usage:
        >>> from vFense.plugins.vuln.redhat.parser import get_msg_links_by_thread
        >>> thread = 'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
        >>> msg_links = get_msg_links_by_thread(thread)

    Returns:
        List of urls
        >>> [
            'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'
        ]
    """

    dlinks = []
    req=requests.get(thread, verify=False)
    if req.ok:
        date = thread.split('/')[-2]
        tsoup=BeautifulSoup(req.text)
        dlinks = (
            map(
                lambda x: os.path.join(URL, date, x.get('href')),
                tsoup.find_all("a", attrs={"name": re.compile("\d+")})
            )
        )

    return(dlinks)

def get_html_content(hlink, force=False):
    """
    Parse the content of Individual RedHat Updates or Message link and return the html contents
    Args:
        hlink (url) : Redhat Update or Message link
        e.g:
        >>> hlink
        'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'

    Basic Usage :
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> content = parse_hdata(hlink)

    Returns:
        html webpage content

    """
    content = None
    msg_location = (
        os.path.join(
            RedhatDataDir.HTML_DIR, '/'.join(hlink.split('/')[-2:])
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

    return(content)

def get_html_latest_content(hlink):
    """
    Parse the content of Individual RedHat Updates or Message link and return the html contents
    Args:
        hlink (url) : Redhat Update or Message link
        e.g:
        >>> hlink
        'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'

    Basic Usage :
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> content = parse_hdata(hlink)

    Returns:
        html webpage content

    """
    content = None
    msg_location = (
        os.path.join(
            RedhatDataDir.HTML_DIR, '/'.join(hlink.split('/')[-2:])
        )
    )

    if not os.path.exists(msg_location):
        request = requests.get(hlink, verify=False)
        if request.ok:
            content = request.content
            msg_file = open(msg_location, 'wb')
            msg_file.write(content)
            msg_file.close()

    return(content)


def make_html_folder(dir_name):
    """
    Verify or Create (if not exist) folder to store the redhat updates (html files) and
    return the PATH name.

    Args:
        dir_name = directory or folder name ('folder-name')

    Basic Usage:

        >>> from vFense.plugins.vuln.redhat._constants import *
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> FPATH = make_html_folder(dname='redhat')

    Returns:

        >>> FPATH
        '/usr/local/lib/python2.7/dist-packages/vFense/plugins/vuln/redhat/data/html/redhat'
        >>>

    """

    fpath = os.path.join(RedhatDataDir.HTML_DIR, dir_name)
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    return(fpath)

def get_apps_info(content):
    """
    Parse the list of rpm packages from the data-file and return as list.
    Args:
        content (str): the html content this function will parse.

    Basic Usage:
        >>> import os
        >>> os.getcwd()
        '/opt/TopPatch/tp/src/plugins/vuln/redhat'
        >>> from vFense.plugins.vuln.redhat.parser import *
        >>> dfile ='data/html/redhat/2010-March/msg00043.html'
        >>> get_rpm_pkgs(dfile=dfile)


    RETURNS:

        List of rpm packages parsed from data file corresponding to redhat updates/
        ['seamonkey-nss-devel-1.0.9-0.52.el3.s390.rpm', 'seamonkey-nss-1.0.9-0.52.el3.s390x.rpm', 'seamonkey-nspr-1.0.9-0.52.el3.s390x.rpm',...]


    """
    rpm_pkgs = []
    data = []
    pkgs = content.split()
    for pkg in pkgs:
        if '.rpm' in pkg:
            if not 'ftp://' in pkg:
                rpm_pkgs.append(pkg)

    rpm_pkgs = list(set(rpm_pkgs))
    for pkg in rpm_pkgs:
        app = RedhatVulnApp()
        if re.search(r'(^[A-Za-z0-9-_]+)?-', pkg):
            app.name = re.search(r'(^[A-Za-z0-9-_]+)?-', pkg).group(1)
            if app.name:
                pkg = re.sub(r'(^[A-Za-z0-9-]+)?-', '', pkg)
                app.version = '.'.join(pkg.split('.')[:-2])
                app.arch = pkg.split('.')[-2]
                app.app_id = build_app_id(app.name, app.version)
                data.append(app.to_dict())

    return data

def get_rh_cve_ids(content):
    """
    Parse cve_ids from the data file and return the list of cve_ids.

    Args:
        content (str): the html content this function will parse.

    Basic Usage:

        >>> import os
        >>> os.getcwd()
        '/opt/TopPatch/tp/src/plugins/vuln/redhat'
        >>> from vFense.plugins.vuln.redhat.parser import *
        >>> cve_ids=get_rh_cve_ids(dfile=dfile)


    RETURNS:
        List of CVE-IDs for specific redhat vulnerability update.
        ['CVE-2010-0174', 'CVE-2010-0175', 'CVE-2010-0176', 'CVE-2010-0177']

    """
    cve_ids = []
    cve_search = re.search(r"CVE\sNames:\s+(\w.*)", content, re.DOTALL)
    if cve_search:
        cve_data = cve_search.group().split(':')[1].strip()
        for cve in cve_data.split():
            if 'CVE-' in cve:
                cve_ids.append(cve)

    cve_id_list = list(set(cve_ids))

    return cve_id_list

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
