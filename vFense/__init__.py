import os
import re
import fnmatch
import importlib
import logging, logging.config
from vFense.supported_platforms import *

VFENSE_BASE_SRC_PATH = os.path.dirname(os.path.realpath(__file__))
VFENSE_BASE_PATH = (
    os.path.realpath(
        os.path.join(
            VFENSE_BASE_SRC_PATH, '..'
        )
    )
)
BIN_DIR = '/usr/local/bin'
VFENSE_INIT_D_PATH = os.path.join(VFENSE_BASE_PATH, 'init.d')
VFENSE_BIN_PATH = os.path.join(VFENSE_BASE_PATH, 'bin')
VFENSE_INIT_D_SCRIPT = os.path.join(VFENSE_INIT_D_PATH, 'vFense')
VFENSE_INIT_D_SYMLINK = '/etc/init.d/vFense'
VFENSED = os.path.join(VFENSE_BIN_PATH, 'vFensed')
VFENSED_SYMLINK = os.path.join(BIN_DIR, 'vFensed')
VFENSE_TEMPLATE_PATH = os.path.join(VFENSE_BASE_PATH, 'templates')
VFENSE_WWW_PATH = os.path.join(VFENSE_BASE_PATH, 'wwwstatic')
VFENSE_SSL_PATH = os.path.join(VFENSE_BASE_PATH, 'data', 'ssl')
VFENSE_PLUGINS_PATH = os.path.join(VFENSE_BASE_SRC_PATH, 'plugins')
VFENSE_VULN_PATH = os.path.join(VFENSE_PLUGINS_PATH, 'vuln')
VFENSE_VAR_PATH = os.path.join(VFENSE_BASE_PATH, 'var')
VFENSE_TMP_PATH = os.path.join(VFENSE_VAR_PATH, 'tmp')
VFENSE_LOG_PATH = os.path.join(VFENSE_VAR_PATH, 'log')
VFENSE_APP_PATH = os.path.join(VFENSE_VAR_PATH, 'packages')
VFENSE_SCHEDULER_PATH = os.path.join(VFENSE_VAR_PATH, 'scheduler')
VFENSE_APP_TMP_PATH = os.path.join(VFENSE_APP_PATH, 'tmp')
VFENSE_APP_DEP_PATH = os.path.join(VFENSE_APP_PATH, 'dependencies')
VFENSE_CONF_PATH = os.path.join(VFENSE_BASE_PATH, 'conf')
VFENSE_LOGGING_CONFIG = os.path.join(VFENSE_CONF_PATH, 'logging.config')
VFENSE_DB_CONFIG = os.path.join(VFENSE_CONF_PATH, 'database.conf')
###RETHINKDB SPECIFIC CONFIG
RETHINK_SOURCE_CONF = os.path.join(VFENSE_CONF_PATH ,'rethinkdb_vFense.conf')
RETHINK_PATH = '/usr/share/rethinkdb'
RETHINK_USER = 'rethinkdb'
RETHINK_INSTANCES_PATH = '/etc/rethinkdb/instances.d'
RETHINK_VFENSE_PATH = '/var/lib/rethinkdb/vFense'
RETHINK_DATA_PATH = os.path.join(RETHINK_VFENSE_PATH, 'data')
RETHINK_CONF = '/etc/rethinkdb/instances.d/vFense.conf'
RETHINK_WEB = '/usr/share/rethinkdb/web'
RETHINK_PID_FILE = '/var/run/rethinkdb/vFense/pid_file'
SCHEDULER_PY = 'apscheduler/scheduler.py'

def get_nginx_config_location():
    config_dir = None
    config = None
    if get_distro() in DEBIAN_DISTROS:
        config_dir = '/etc/nginx/sites-enabled/'
    elif get_distro() in REDHAT_DISTROS:
        config_dir = '/etc/nginx/conf.d/'

    if config_dir:
        config = os.path.join(config_dir, 'vFense.conf')

    return config


def get_sheduler_location():
    sched_location = ''
    for site in SITE_PACKAGES:
        sched_location = site + '/' + SCHEDULER_PY
        if os.path.exists(sched_location):
            return(sched_location)
    return(sched_location)


def import_modules_by_regex(regex):
    """Import vFense python modules by regex
    Args:
        regex (str): The file you want to import.
            example.. _db_init.py
    """
    db_files = []
    for root, dirs, files in os.walk(VFENSE_BASE_PATH):
        for filename in fnmatch.filter(files, regex):
            file_path = (
                re.search(r'vFense/(vFense.*).py', os.path.join(root, filename))
            )
            if file_path:
                module = file_path.group(1).replace('/', '.')
                db_files.append(module)
                importlib.import_module(module)
    return db_files



class Base(object):
    """Used to represent an instance of an agent."""

    def __init__(self):
        pass


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values."""
        pass


    def get_invalid_fields(self):
        """Check for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.
        """
        invalid_fields = []

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary."""

        return {}

    def to_dict_non_null(self):
        """ Use to get non None fields. Useful when
        filling out just a few fields to update the db with .

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        agent_dict = self.to_dict()

        return {k:agent_dict[k] for k in agent_dict}
