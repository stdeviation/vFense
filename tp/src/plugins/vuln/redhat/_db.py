import logging
import logging.config
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln import *
from vFense.plugins.vuln._constants import *
from vFense.plugins.vuln.redhat import *
from vFense.plugins.vuln.redhat._constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

@time_it
@db_create_close
def get_redhat_vulnerability_data_by_vuln_id(vuln_id, conn=None):
    info = {}
    map_hash = (
        {
            RedhatSecurityBulletinKey.BulletinId: r.row[RedhatSecurityBulletinKey.BulletinId],
            RedhatSecurityBulletinKey.DatePosted: r.row[RedhatSecurityBulletinKey.DatePosted],
            RedhatSecurityBulletinKey.Details: r.row[RedhatSecurityBulletinKey.Details],
            RedhatSecurityBulletinKey.CveIds: r.row[RedhatSecurityBulletinKey.CveIds],
            RedhatSecurityBulletinKey.Apps: r.row[RedhatSecurityBulletinKey.Apps],
            RedhatSecurityBulletinKey.Product : r.row[RedhatSecurityBulletinKey.Product],
            RedhatSecurityBulletinKey.AppsLink : r.row[RedhatSecurityBulletinKey.AppsLink],
            #WindowsSecurityBulletinKey.Supersedes: [],
        }
    )
    try:
        info = list(
            r
            .table(RedHatSecurityCollection.Bulletin)
            .get_all(vuln_id, index=RedhatSecurityBulletinIndexes.BulletinId)
            .map(map_hash)
            .run(conn)
        )
        if info:
            info = info[0]

    except Exception as e:
        logger.exception(e)

    return(info)



@time_it
@db_create_close
#@return_status_tuple
def insert_bulletin_data(bulletin_data, conn=None):
    """Insert Redhat Bulletin data into the Redhat Security Bulletin Collection
        DO NOT CALL DIRECTLY
    Args:
        bulletin_data (list|dict): List or dictionary of vulnerability data

    Basic Usage:

    Returns:
    """

    data = {}
    try:
        data = (
            r
            .table(RedHatSecurityCollection.Bulletin)
            .insert(bulletin_data, upsert=True)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)



