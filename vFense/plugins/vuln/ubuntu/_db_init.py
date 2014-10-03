import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln.ubuntu._db_model import (
    UbuntuVulnerabilityCollections, UbuntuVulnerabilityKeys,
    UbuntuVulnerabilityIndexes
)
from vFense.plugins.vuln.ubuntu._constants import UbuntuVulnSubKeys
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

@db_create_close
def initialize_ubuntu_indexes(collection, indexes, conn=None):
    if not UbuntuVulnerabilityIndexes.CveIds in indexes:
        (
            r
            .table(collection)
            .index_create(
                UbuntuVulnerabilityIndexes.CveIds,
                multi=True
            )
            .run(conn)
        )

    if not UbuntuVulnerabilityIndexes.NameAndVersion in indexes:
        (
            r
            .table(collection)
            .index_create(
                UbuntuVulnerabilityIndexes.NameAndVersion,
                lambda x:
                x[UbuntuVulnerabilityKeys.Apps].map(
                    lambda y:
                    [
                        y[UbuntuVulnSubKeys.NAME],
                        y[UbuntuVulnSubKeys.VERSION]
                    ]
                ), multi=True
            )
            .run(conn)
        )

    if not UbuntuVulnerabilityIndexes.AppId in indexes:
        (
            r
            .table(collection)
            .index_create(
                UbuntuVulnerabilityIndexes.AppId,
                lambda x:
                x[UbuntuVulnerabilityKeys.Apps].map(
                    lambda y: y[UbuntuVulnSubKeys.APP_ID]
                ), multi=True
            )
            .run(conn)
        )

try:
    ubuntu_collections = [
        (
            UbuntuVulnerabilityCollections.Vulnerabilities,
            UbuntuVulnerabilityKeys.VulnerabilityId
        ),
    ]
    current_collections = retrieve_collections()
    for collection in ubuntu_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_ubuntu_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
