from bs4 import BeautifulSoup
import requests
import re
import sys
import logging
import logging.config
from time import mktime, sleep
from datetime import datetime

from vFense.db.client import r

from vFense.utils.common import month_to_num_month
from vFense.plugins.vuln import *
from vFense.plugins.vuln.redhat._constants import *
from vFense.plugins.vuln.redhat._db import *
from vFense.plugins.vuln.common import build_bulletin_id

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

URL = REDHAT_ARCHIVE

def get_threads():
    
    """
    Parse the Redhat Officlial Annouces (URL: "https://www.redhat.com/archives/rhsa-announce/") and 
    return the list of threads
    
    BASIC USAGE:
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> threads = get_threads()

    RETURNS:
        >>> threads[0]
        'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
        >>> 
    
    """
    
    threads=[]
    req = requests.get(URL)
    soup= BeautifulSoup(req.text)
    for link in soup.find_all('a'):
        href=link.get('href')
        if "thread" in href:
            threads.append(URL+href)
    rh_threads = list(set(threads))
    return(rh_threads)

def get_dlinks(thread):
    """
    Parse the Redhat update thread link and return the list of data link or message link.
    Args:
        thread (url) : This should be valid Redhat thread link.
        e.g:
        >>> thread
        'https://www.redhat.com/archives/rhsa-announce/2014-April/thread.html'
    
    BASIC USAGE:
    >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
    >>> dlinks=get_dlinks(thread)
    
    RETURNS:
        >>> dlinks[0]
        'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'
        >>> 
    """
    
    dlinks = []
    req=requests.get(thread)
    if req.ok:
        date = thread.split('/')[-2]
        tsoup=BeautifulSoup(req.text)
        for mlink in tsoup.find_all('a'):
             if "msg" in mlink.get('href'):
                 hlink = (URL +date + '/' + mlink.get('href'))
                 dlinks.append(hlink)

    rh_data_links = list(set(dlinks))
    return(rh_data_links)
    
def parse_hdata(hlink):
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
    uri=hlink
    request=requests.get(uri)
    if request.ok:
        content=request.content
    return(content)

def make_html_folder(dname):
    """
    Verify or Create (if not exist) folder to store the redhat updates (html files) and 
    return the PATH name.
    
    Args:
        dname = directory or folder name ('folder-name')
    
    Basic Usage:
    
        >>> from vFense.plugins.vuln.redhat._constants import *
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> FPATH = make_html_folder(dname='redhat')
    
    Returns:
    
        >>> FPATH
        '/usr/local/lib/python2.7/dist-packages/vFense/plugins/vuln/redhat/data/html/redhat'
        >>>  
    
    """
    
    PATH = RedhatDataDir.HTML_DIR 
    DIR = dname
    fpath = (PATH + DIR)
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    return(fpath)
    
def write_content_to_file(file_path, file_name, content=None):
    """
    This will write the content of redhat updates to the specified location locally on server
    and returns the data file. 
    
    ARGS:
        file_path : Specified path to locate the file to write
        file_name : Name of the file to write the content
        content : Content to write the file 
    
    Basic Usage:
        >>> from vFense.plugins.vuln.redhat._constants import *
        >>> from vFense.plugins.vuln.redhat.get_all_redhat_updates import *
        >>> PATH = make_html_folder(dname='redhat')
        >>> PATH
        '/usr/local/lib/python2.7/dist-packages/vFense/plugins/vuln/redhat/data/html/redhat'
        >>> hlink
        'https://www.redhat.com/archives/rhsa-announce/2014-April/msg00016.html'
        >>> content = parse_hdata(hlink)
        >>> file_name = hlink.split('/')[-1]
        >>> file_name
        'msg00016.html'
        >>> data_file = write_content_to_file(file_path=PATH, file_name=file_name, content = content)
        
     Returns:   
        >>> data_file
        '/usr/local/lib/python2.7/dist-packages/vFense/plugins/vuln/redhat/data/html/redhat/msg00016.html'
        >>> 
    
    """
    dfile = (file_path + '/' + file_name)
    if not os.path.exists(dfile):
        msg_file = open(dfile, 'wb')
        content = content
	if content:
            msg_file.write(content)
            msg_file.close()
    return(dfile)

def get_rpm_pkgs(dfile):
    """
    Parse the list of rpm packages from the data-file and return as list.
    ARGS:
        dfile : data file to parse the rpm package for specific redhat vulnerability updates
    
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
    ftp_rpms = []
    datafile=dfile
    if os.stat(datafile).st_size > 0:
        fo=open(datafile, 'r+')
        data=fo.read()
        fo.close()
        if data:
            pkg_info = data
            pkgs = pkg_info.split()
            for pkg in pkgs:
                if '.rpm' in pkg:
                    if 'ftp://' in pkg:
                        ftp_rpms.append(pkg)
                    else:
                        rpm_pkgs.append(pkg)
    
    rpm_packages = list(set(rpm_pkgs))
    ftp_packages = list(set(ftp_rpms))
    data = {
            'rpm_packages': rpm_packages,
            'ftp_packages': ftp_packages,
        }
        
    if not rpm_packages:
        print datafile
    
    return(data)

def get_rh_cve_ids(dfile):
    """
    Parse cve_ids from the data file and return the list of cve_ids.
    
    ARGS:
        dfile : data file to parse the cve-ids for specific redhat vulnerabilty updates.
    
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
    datafile=dfile
    if os.stat(datafile).st_size > 0:
        fo=open(datafile, 'r+')
        data=fo.read()
        cves=(re.search(r"CVE\sNames:\s+(\w.*)", data,re.DOTALL))
        if cves:
            cve_data = (cves.group()).split(':')[1].strip()
            for cve in cve_data.split():
                if 'CVE-' in cve:
                    cve_ids.append(cve)
    cve_id_list = list(set(cve_ids))
    return(cve_id_list)
            
def get_rh_data(dfile):
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
   
        >>> rh_data['bulletin_id']
        'RHSA-2010:0333-01'
        >>> rh_data.keys()
        ['product', 'bulletin_details', 'bullentin_summary', 'bulletin_id', 'solutions', 'references', 'support_url', 'cve_ids', 'apps', 'date_posted']
        >>> 
    
    """
    
    datafile=dfile
    if os.stat(datafile).st_size > 0:
        fo=open(datafile, 'r+')
        data=fo.read()

        summary = None
        smry = re.search('1\.\s+Summary:\n\n(\w.*)\n\n.*2.', data, re.DOTALL)
        if smry:
            summary = smry.group(1)

        descriptions = None
        desc=(re.search('Description:\n\n(\w.*)\n\n.*\s+Solution', data, re.DOTALL))
        if desc:
            descriptions=desc.group(1)
	
        solutions = None
        sol = (re.search('Solution:\n\n(\w.*)\n\n.*\.\s+Bugs fixed', data, re.DOTALL))
        if sol:
            solutions=sol.group(1)
        #bug_fixed=re.search('5\.\s+Bugs fixed:\n\n(\w.*)\n\n.*6\.\s+Package List', data, re.DOTALL).group(1)
        
        pkg_list = get_rpm_pkgs(dfile=dfile)
        if pkg_list:
            rpm_packages = pkg_list['rpm_packages']
            ftp_packages = pkg_list['ftp_packages']
	
        references = None
        ref = (re.search('References:\n\n(\w.*)\n\n.*\.\s+Contact', data, re.DOTALL))        
        if ref:
            references=ref.group(1)

        vulnerability_id = None
        aid = (re.search(r'Advisory\sID:.*', data))
        if aid:
            vulnerability_id = (aid.group()).split(':', 1)[1].strip()
        
        product = None
        prod=(re.search(r"Product:\s.*", data))
        if prod:
            product=prod.group().split(':',1)[1].strip()
        
        reference_url = None
        aurl=re.search(r"Advisory\sURL:\s.*", data)
        if aurl:
	        reference_url=aurl.group().split(':',1)[1].strip()
	    
        date_posted = None
        idate=(re.search(r"Issue\sdate:\s.*", data))
        if idate:
            issue_date=idate.group().split(':',1)[1].strip()
            date_posted = datetime.strptime(issue_date, "%Y-%m-%d").strftime('%s')
	    
        cve_ids = get_rh_cve_ids(dfile=dfile)
        
        parse_data={
            "date_posted": date_posted,
            "bulletin_id":vulnerability_id,
            "bullentin_summary": summary,
            "bulletin_details": descriptions,
            "apps" : rpm_packages,
            "solution_apps": ftp_packages,
            "cve_ids": cve_ids,
            "support_url": reference_url,
            "solutions": solutions,
            "references": references,
            "product":product,
            }
    	return(parse_data)
    
def insert_data_to_db(thread):
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
    cve_updates = []
    data_links = get_dlinks(thread)
    if data_links:
        date=thread.split('/')[-2]
        fpath = make_html_folder(dname=date)
        
        for link in data_links:
            hlink = link
            print hlink
            fname = (hlink.split('/')[-1])
            pre_data=parse_hdata(hlink)
            dfile = write_content_to_file(file_path=fpath, file_name=fname, content=pre_data)
            cve_data = get_rh_data(dfile)
            if cve_data:
                cve_updates.append(cve_data)
        
        insert=insert_bulletin_data(bulletin_data=cve_updates)
        return(insert)


def update_all_redhat_data():
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
            pre_updates = insert_data_to_db(thread)
