import os

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
