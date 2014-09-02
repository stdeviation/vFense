import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln.redhat._db_model import (
    RedhatVulnerabilityKeys, RedHatVulnerabilityCollections,
    RedhatVulnerabilityIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

@time_it
@db_create_close
def get_redhat_vulnerability_data_by_vuln_id(vuln_id, conn=None):
    info = {}
    map_hash = (
        {
            RedhatVulnerabilityKeys.VulnerabilityId: r.row[RedhatVulnerabilityKeys.VulnerabilityId],
            RedhatVulnerabilityKeys.DatePosted: r.row[RedhatVulnerabilityKeys.DatePosted],
            RedhatVulnerabilityKeys.Details: r.row[RedhatVulnerabilityKeys.Details],
            RedhatVulnerabilityKeys.CveIds: r.row[RedhatVulnerabilityKeys.CveIds],
            RedhatVulnerabilityKeys.Apps: r.row[RedhatVulnerabilityKeys.Apps],
            RedhatVulnerabilityKeys.Product : r.row[RedhatVulnerabilityKeys.Product],
            RedhatVulnerabilityKeys.AppsLink : r.row[RedhatVulnerabilityKeys.AppsLink],
        }
    )
    try:
        info = list(
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .get_all(vuln_id)
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
@return_status_tuple
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
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .insert(bulletin_data, conflict="replace")
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
