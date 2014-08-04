import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.decorators import time_it
from vFense.plugins.patching._db_files import file_data_exists, \
    update_file_data, insert_file_data

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
def add_file_data(file_data):
    """Insert or Update the file data information for application id.

    Args:
        file_data (list): List of Files instances.

    Basic Usage:
        >>> from vFense.plugins.patching.file_data import add_file_data
        >>> app_id = '3e480d178a945e8c35479c60a398da3d16a0f8c2aecf3306b2341466b5e897ae'
        >>> agent_id = '272ce70a-6cb1-4903-b395-bba4386a5171'
        >>> file_data = [
            {
                "file_hash": "d9af1cb42d87235d83aadeb014a542105ee7eea99fe45bed594b27008bb2c10c",
                "file_name": "gwibber-service-facebook_3.4.2-0ubuntu2.4_all.deb",
                "file_uri": "http://us.archive.ubuntu.com/ubuntu/pool/main/g/gwibber/gwibber-service-facebook_3.4.2-0ubuntu2.4_all.deb",
                "file_size": 7782
            }
        ]

    Returns:
        Boolean
    """
    data_to_insert = []
    data_inserted = False
    print len(file_data)
    for fd in file_data:
        if file_data_exists(fd.file_name):
            if fd.agent_ids:
                update_file_data(fd.file_name, agent_ids=fd.agent_ids)
                data_inserted = True

            elif fd.app_ids:
                update_file_data(fd.file_name, app_ids=fd.app_ids)
                data_inserted = True
        else:
            fd.fill_in_defaults()
            data_to_insert.append(fd.to_dict())

    if data_to_insert:
        insert_file_data(data_to_insert)

    return data_inserted
