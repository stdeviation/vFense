import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln.redhat._db_model import (
    RedHatVulnerabilityCollections, RedhatVulnerabilityKeys,
    RedhatVulnerabilityIndexes
)
from vFense.plugins.vuln.redhat._constants import RedhatVulnSubKeys
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

@db_create_close
def initialize_redhat_indexes(collection, indexes, conn=None):
    if not RedhatVulnerabilityIndexes.CveIds in indexes:
        (
            r
            .table(collection)
            .index_create(
                RedhatVulnerabilityIndexes.CveIds,
                multi=True
            )
            .run(conn)
        )

    if not RedhatVulnerabilityIndexes.NameAndVersion in indexes:
        (
            r
            .table(collection)
            .index_create(
                RedhatVulnerabilityIndexes.NameAndVersion,
                lambda x:
                x[RedhatVulnerabilityKeys.Apps].map(
                    lambda y:
                    [
                        y[RedhatVulnSubKeys.NAME],
                        y[RedhatVulnSubKeys.VERSION]
                    ]
                ), multi=True
            )
            .run(conn)
        )

    if not RedhatVulnerabilityIndexes.AppId in indexes:
        (
            r
            .table(collection)
            .index_create(
                RedhatVulnerabilityIndexes.AppId,
                lambda x:
                x[RedhatVulnerabilityKeys.Apps].map(
                    lambda y: y[RedhatVulnSubKeys.APP_ID]
                ), multi=True
            )
            .run(conn)
        )

try:
    redhat_collections = [
        (
            RedHatVulnerabilityCollections.Vulnerabilities,
            RedhatVulnerabilityKeys.VulnerabilityId
        ),
    ]
    current_collections = retrieve_collections()
    for collection in redhat_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_redhat_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
