import logging
import logging.config

from vFense.core.decorators import time_it
from vFense.plugins.patching import FilesKey
from vFense.plugins.patching._db_files import file_data_exists, \
    update_file_data, insert_file_data

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
def add_file_data(app_id, file_data, agent_id=None):
    """Insert or Update the file date information for
        application id.

    Args:
        app_id (str): The 64 character hex digest of the application.
        file_data (list): List of dictionaries

    Kwargs:
        agent_id (str): The 36 character UUID of the agent.

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
    """
    data_to_insert = []
    data_to_update = []
    for uri in file_data:
        if file_data_exists(uri[FilesKey.FileName]):
            data_to_update.append(uri)
        else:
            data_to_insert.append(uri)

    if data_to_insert:
        print  'inserting data',  data_to_insert
        insert_file_data(app_id, data_to_insert, agent_id)

    elif data_to_update:
        print  'updating data',  data_to_update
        print app_id, agent_id
        insert_file_data(app_id, data_to_insert, agent_id)
        update_file_data(app_id, data_to_insert, agent_id)
