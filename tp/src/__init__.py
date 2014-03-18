import os
from vFense.supported_platforms import *

RETHINK_PATH = '/usr/share/rethinkdb'
RETHINK_USER = 'rethinkdb'
RETHINK_INSTANCES_PATH = '/etc/rethinkdb/instances.d'
RETHINK_DATA_PATH = '/var/lib/rethinkdb/vFense/data'
RETHINK_SOURCE_CONF = '/opt/TopPatch/conf/rethinkdb_vFense.conf'
RETHINK_CONF = '/etc/rethinkdb/instances.d/vFense.conf'
RETHINK_WEB = '/usr/share/rethinkdb/web'
RETHINK_PID_FILE = '/var/run/rethinkdb/vFense/pid_file'
TOPPATCH_HOME = '/opt/TopPatch/'
SCHEDULER_PY = 'apscheduler/scheduler.py'

def get_nginx_config_location():
    config_dir = None
    config = None
    if get_distro() in DEBIAN_DISTROS:
        config_dir = '/etc/nginx/sites-enabled/'
    elif get_distro() in REDHAT_DISTROS:
        config_dir = '/etc/nginx/conf.d/'

    if config_dir:
        config = config_dir + 'vFense.conf'

    return config


def get_sheduler_location():
    sched_location = ''
    for site in site_packages:
        sched_location = site + '/' + SCHEDULER_PY
        if os.path.exists(sched_location):
            return(sched_location)
    return(sched_location)

