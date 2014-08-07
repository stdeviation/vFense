import os
import re
import gc
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from time import mktime
from datetime import datetime

from xlrd import open_workbook, xldate_as_tuple

from vFense.plugins.vuln.windows import Windows, WindowsVulnApp
from vFense.plugins.vuln.windows._constants import (
    WindowsVulnSubKeys, WindowsDataDir, WindowsBulletinStrings
)
from vFense.plugins.vuln.windows._db import insert_bulletin_data
from vFense.plugins.vuln.windows.downloader import download_latest_xls_from_msft

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

def parse_spread_sheet(bulletin_file):
    """Parse the entire microsoft excel bulleting data and
        return the data, ready to be inserted into the database.
    Args:
        bulletin_file (str): The file location on disk
    Returns:
        List of dictionairies
    """
    count = 0
    data_to_store = []
    workbook = open_workbook(bulletin_file)
    sheet = workbook.sheet_by_name(WindowsBulletinStrings.WORKBOOK_SHEET)
    rows = range(sheet.nrows)
    rows.pop(0)
    vuln = Windows()
    vuln.fill_in_defaults()
    for i in rows:
        row = sheet.row_values(i)
        if row[7] != '':
            row[7] = 'KB' + str(int(row[7]))

        if row[2] != '':
            row[2] = 'KB' + str(int(row[2]))

        if vuln.vulnerability_id != row[1]:
            if count > 0:
                data_to_store.append(vuln.to_dict_db())
            count = count + 1
            del(vuln)
            vuln = Windows()
            vuln.fill_in_defaults()

        date = xldate_as_tuple(row[0], workbook.datemode)
        epoch_time = mktime(datetime(*date).timetuple())
        vuln.vulnerability_id = row[1]
        vuln.kb = row[2]
        vuln.severity = row[3]
        vuln.impact = row[4]
        vuln.details = row[5]
        vuln.date_posted = epoch_time

        app = WindowsVulnApp()
        app.fill_in_defaults()
        app.product = row[6]
        app.kb = row[7]
        app.component = row[8]
        app.impact = row[9]
        app.severity = row[10]

        if len(row) == 15:
            supercedes = row[12]
            reboot = row[13]
            cve_ids = row[14].split(',')
        else:
            supercedes = row[11]
            reboot = row[12]
            cve_ids = row[13].split(',')

        vuln.cve_ids = list(set(vuln.cve_ids).intersection(cve_ids))
        app.reboot = reboot
        info = supercedes.split(',')
        for j in info:
            bulletin_data = j.split('[')
            if len(bulletin_data) > 1:
                vulnerability_id = bulletin_data[0]
                kb = re.sub('^', 'KB', bulletin_data[1][:-1])
            else:
                vulnerability_id = bulletin_data[0]
                kb = None

            if kb and vulnerability_id:
                app.supercedes.append(
                    {
                        WindowsVulnSubKeys.VULNERABILITY_ID: vulnerability_id,
                        WindowsVulnSubKeys.KB: kb
                    }
                )
        vuln.apps.append(app.to_dict())
        print len(vuln.apps)

        if count == 3:
            return data_to_store

    return(data_to_store)

def parse_bulletin_and_updatedb():
    """Download the Bulletin and parse it and insert into the database
    """
    logger.info('starting microsoft security bulletin update process')
    if not os.path.exists(WindowsDataDir.XLS_DIR):
        os.makedirs(WindowsDataDir.XLS_DIR, 0755)
    downloaded, xls_file = download_latest_xls_from_msft()
    if downloaded:
        bulletin_data = parse_spread_sheet(xls_file)
        print len(bulletin_data)
        #insert_bulletin_data(bulletin_data)
        return bulletin_data

    logger.info('finished microsoft security bulletin update process')
    gc.collect()

#parse_bulletin_and_updatedb()
