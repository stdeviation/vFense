import re
import sys
import logging
import logging.config
from vFense.db.client import db_create_close, r, db_connect
from vFense.plugins.cve import *
from vFense.plugins.cve.cve_constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

@db_create_close
def get_win_vulnerability_data_by_vuln_id(vuln_id, conn=None):
    info = {}
    map_hash = (
        {
            WindowsSecurityBulletinKey.Id: r.row[WindowsSecurityBulletinKey.Id],
            WindowsSecurityBulletinKey.BulletinId: r.row[WindowsSecurityBulletinKey.BulletinId],
            WindowsSecurityBulletinKey.DatePosted: r.row[WindowsSecurityBulletinKey.DatePosted].to_epoch_time(),
            WindowsSecurityBulletinKey.Details: r.row[WindowsSecurityBulletinKey.Details],
            WindowsSecurityBulletinKey.CveIds: r.row[WindowsSecurityBulletinKey.CveIds],
            WindowsSecurityBulletinKey.Supersedes: r.row[WindowsSecurityBulletinKey.Supersedes],
        }
    )
    try:
        info = list(
            r
            .table(WindowsSecurityBulletinCollection)
            .get_all(vuln_id, index=WindowsSecurityBulletinIndexes.BulletinId)
            .map(map_hash)
            .run(conn)
        )
        if info:
            info = info[0]

    except Exception as e:
        logger.exception(e)

    return(info)


@db_create_close
def get_ubu_vulnerability_data_by_vuln_id(vuln_id, conn=None):
    info = {}
    map_hash = (
        {
            UbuntuSecurityBulletinKey.Id: r.row[UbuntuSecurityBulletinKey.Id],
            UbuntuSecurityBulletinKey.BulletinId: r.row[UbuntuSecurityBulletinKey.BulletinId],
            UbuntuSecurityBulletinKey.DatePosted: r.row[UbuntuSecurityBulletinKey.DatePosted].to_epoch_time(),
            UbuntuSecurityBulletinKey.Details: r.row[UbuntuSecurityBulletinKey.Details],
            UbuntuSecurityBulletinKey.CveIds: r.row[UbuntuSecurityBulletinKey.CveIds],
            WindowsSecurityBulletinKey.Supersedes: [],
        }
    )
    try:
        info = list(
            r
            .table(UbuntuSecurityBulletinCollection)
            .get_all(vuln_id, index=UbuntuSecurityBulletinIndexes.BulletinId)
            .map(map_hash)
            .run(conn)
        )
        if info:
            info = info[0]

    except Exception as e:
        logger.exception(e)

    return(info)

@db_create_close
def get_cve_data_by_cve_id(cve_id, conn=None):
    info = {}
    map_hash = (
        {
            CveKey.CveId: r.row[CveKey.CveId],
            CveKey.CveCategories: r.row[CveKey.CveCategories],
            CveKey.CveDescriptions: r.row[CveKey.CveDescriptions],
            CveKey.CveRefs: r.row[CveKey.CveRefs],
            CveKey.CveSev: r.row[CveKey.CveSev],
            CveKey.CvssScore: r.row[CveKey.CvssScore],
            CveKey.CvssBaseScore: r.row[CveKey.CvssBaseScore],
            CveKey.CvssImpactSubScore: r.row[CveKey.CvssImpactSubScore],
            CveKey.CvssExploitSubScore: r.row[CveKey.CvssExploitSubScore],
            CveKey.CvssVector: r.row[CveKey.CvssVector],
            CveKey.CvePublishedDate: r.row[CveKey.CvePublishedDate].to_epoch_time(),
            CveKey.CveModifiedDate: r.row[CveKey.CveModifiedDate].to_epoch_time(),
        }
    )
    try:
        info = (
            r
            .table(CveCollection)
            .get_all(cve_id)
            .map(map_hash)
            .run(conn)
        )
        if info:
            info = info[0]

    except Exception as e:
        logger.exception(e)

    return(info)

