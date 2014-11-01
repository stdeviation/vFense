import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
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
def fetch_vuln_ids(name, version, os_string, conn=None):
    """Retrieve RedHat RHSA IDS and CVE_IDS for an Application
    Args:
        name (str): The name of the application
        version (str): The version of the application
        os_string (str): The Version of Ubuntu (Ubuntu 12.04 LTS)

    Basic Usage:
        >>> from vFense.plugins.vuln.redhat._db import fetch_ubuntu_vuln_ids
        >>> name = 'nvidia-173'
        >>> version = '173.14.22-0ubuntu11.2'
        >>> os_string = 'Ubuntu 10.04 LTS'
        >>> fetch_vuln_ids(name, version, os_string)

    Returns:
        Dictionary
        {
            "cve_ids": [],
            "bulletin_id": "USN-1523-1"
        }
    """
    data = []
    try:
        data = list(
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .get_all(
                [name, version],
                index=RedhatVulnerabilityIndexes.NameAndVersion
            )
            .pluck(RedhatVulnerabilityKeys.VulnerabilityId, UbuntuVulnerabilityKeys.CveIds)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_vuln_data(vuln_id, conn=None):
    info = {}
    merge_hash = (
        {
            RedhatVulnerabilityKeys.DatePosted: (
                r.row[RedhatVulnerabilityKeys.DatePosted].to_epoch_time()
            ),
        }
    )
    try:
        info = list(
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .get_all(vuln_id)
            .merge(merge_hash)
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
