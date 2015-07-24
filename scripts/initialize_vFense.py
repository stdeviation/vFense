import argparse
import ConfigParser
import os
import pwd
import shutil
import subprocess
import sys
from time import sleep
from _magic import *
from vFense._constants import (
    VFENSE_BASE_SRC_PATH, VFENSE_BASE_PATH, VFENSE_APP_PATH,
    VFENSE_LOG_PATH, VFENSE_LOGGING_CONFIG, VFENSE_VULN_PATH,
    VFENSE_APP_TMP_PATH, VFENSE_SCHEDULER_PATH, RETHINK_CONF,
    VFENSE_TMP_PATH, VFENSED_SYMLINK, VFENSED, VFENSE_BASE_PATH,
    VFENSE_INIT_D_SCRIPT, VFENSE_INIT_D_SYMLINK, VFENSE_CONFIG,
    VFENSE_SSL_PATH, RETHINK_VFENSE_PATH, RETHINK_PATH, RETHINK_SOURCE_CONF
)
from vFense.core.logger.logger import vFenseLogger
vfense_logger = vFenseLogger()
vfense_logger.create_config()

import logging, logging.config

from vFense.utils.common import import_modules_by_regex
import nginx_config_creator as ncc
from vFense.utils.supported_platforms import (
    REDHAT_DISTROS, DEBIAN_DISTROS, get_distro, SITE_PACKAGES
)
from vFense.utils.security import generate_pass, check_password
from vFense.utils.ssl_initialize import generate_generic_certs
from vFense.utils.common import pick_valid_ip_address
from vFense.db.client import db_connect, r, db_create_close
from vFense.core.user import User
from vFense.core.user.manager import UserManager
from vFense.core.user._constants import DefaultUsers
from vFense.core.group import Group
from vFense.core.group.manager import GroupManager
from vFense.core.group._constants import DefaultGroups
from vFense.core.view import View
from vFense.core.view.manager import ViewManager
from vFense.core.view._constants import DefaultViews
from vFense.core.permissions._constants import Permissions

from vFense.plugins.vuln.cve.parser import load_up_all_xml_into_db
from vFense.plugins.vuln.windows.parser import parse_bulletin_and_updatedb
from vFense.plugins.vuln.ubuntu.list_parser import ubuntu_archive_processor
from vFense.plugins.vuln.redhat.list_parser import redhat_archive_processor

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

Config = ConfigParser.ConfigParser()
Config.read(VFENSE_CONFIG)

if os.getuid() != 0:
    print 'MUST BE ROOT IN ORDER TO RUN'
    sys.exit(1)

parser = argparse.ArgumentParser(description='Initialize vFense Options')
parser.add_argument(
    '--ipaddress', dest='ip_address', default=pick_valid_ip_address(),
    help='Pass the IP Address of the patching Server'
)
parser.add_argument(
    '--password', dest='admin_password', default=generate_pass(),
    help='Pass the password to use for the admin User. Default is a random generated password'
)
parser.add_argument(
    '--cve-data', dest='cve_data', action='store_true',
    help='Initialize CVE data. This is the default.'
)
parser.add_argument(
    '--no-cve-data', dest='cve_data', action='store_false',
    help='Not to initialize CVE data. This is for testing purposes.'
)
parser.set_defaults(cve_data=True)

args = parser.parse_args()

if args.admin_password:
    password_validated = check_password(args.admin_password)
    if not password_validated[0]:
        print (
            'Password failed to meet the minimum requirements.\n' +
            'Uppercase, Lowercase, Numeric, Special ' +
            'and a minimum of 8 characters.\nYour password: %s is %s' %
            (args.admin_password, password_validated[1])
        )
        sys.exit(1)

if Config.get("vFense", "hostname"):
    url = 'https://%s/packages/' % (args.dns_name)
    nginx_server_name = args.dns_name
else:
    url = 'https://%s/packages/' % (args.ip_address)
    nginx_server_name = args.ip_address

def build_nginx_config():
    generate_generic_certs()
    ncc.nginx_config_builder(
        nginx_server_name
    )


def create_directories():
    if not os.path.exists(VFENSE_SSL_PATH):
        os.mkdir(VFENSE_SSL_PATH, 0755)
    if not os.path.exists(VFENSE_LOG_PATH):
        os.mkdir(VFENSE_LOG_PATH, 0755)
    if not os.path.exists(VFENSE_SCHEDULER_PATH):
        os.mkdir(VFENSE_SCHEDULER_PATH, 0755)
    if not os.path.exists(VFENSE_APP_PATH):
        os.mkdir(VFENSE_APP_PATH, 0755)
    if not os.path.exists(VFENSE_APP_TMP_PATH):
        os.mkdir(VFENSE_APP_TMP_PATH, 0775)
    if not os.path.exists(os.path.join(VFENSE_VULN_PATH, 'windows/data/xls')):
        os.makedirs(os.path.join(VFENSE_VULN_PATH, 'windows/data/xls'), 0755)
    if not os.path.exists(os.path.join(VFENSE_VULN_PATH, 'cve/data/xml')):
        os.makedirs(os.path.join(VFENSE_VULN_PATH,'cve/data/xml'), 0755)
    if not os.path.exists(os.path.join(VFENSE_VULN_PATH, 'ubuntu/data/html')):
        os.makedirs(os.path.join(VFENSE_VULN_PATH, 'ubuntu/data/html'), 0755)

def create_symlinks():
    try:
        if os.path.exists(os.path.join(SITE_PACKAGES[-1], 'vFense')):
            os.remove(os.path.join(SITE_PACKAGES[-1], 'vFense'))

        elif (
                not os.path.exists(
                    os.readlink(os.path.join(SITE_PACKAGES[-1], 'vFense'))
                )
            ):
            os.remove(os.path.join(SITE_PACKAGES[-1], 'vFense'))

    except Exception as e:
        pass

    subprocess.Popen(
        [
            'ln', '-s', VFENSE_BASE_SRC_PATH, SITE_PACKAGES[-1]
        ],
    )

    try:
        if os.path.exists(VFENSED_SYMLINK):
            os.remove(VFENSED_SYMLINK)

        elif not os.path.exists(os.readlink(VFENSED_SYMLINK)):
            os.remove(VFENSED_SYMLINK)

    except Exception as e:
        pass

    subprocess.Popen(
        [
            'ln', '-s', VFENSED, VFENSED_SYMLINK
        ],
    )

    try:
        if os.path.exists(VFENSE_INIT_D_SYMLINK):
            os.remove(VFENSE_INIT_D_SYMLINK)

        elif not os.path.exists(os.readlink(VFENSE_INIT_D_SYMLINK)):
            os.remove(VFENSE_INIT_D_SYMLINK)

    except Exception as e:
        pass

    subprocess.Popen(
        [
            'ln', '-s',
            VFENSE_INIT_D_SCRIPT,
            VFENSE_INIT_D_SYMLINK
        ],
    )

    if get_distro() in DEBIAN_DISTROS:
        subprocess.Popen(
            [
                'update-rc.d', 'vFense',
                'defaults'
            ],
        )

    if get_distro() in REDHAT_DISTROS:
        if os.path.exists('/usr/bin/rqworker'):
            subprocess.Popen(
                [
                    'ln', '-s',
                    '/usr/bin/rqworker',
                    '/usr/local/bin/rqworker'
                ],
            )


def add_local_user():
    try:
        pwd.getpwnam('vfense')

    except Exception as e:
        if get_distro() in DEBIAN_DISTROS:
            subprocess.Popen(
                [
                    'adduser', '--disabled-password', '--gecos', '', 'vfense',
                ],
            )
        elif get_distro() in REDHAT_DISTROS:
            subprocess.Popen(
                [
                    'useradd', 'vfense',
                ],
            )


@db_create_close
def create_views(conn=None):
    view = View(
        view_name=DefaultViews.GLOBAL,
        server_queue_ttl=Config.get("vFense", "server_queue_ttl"),
        package_download_url_base=url
    )
    view_manager = ViewManager(view.view_name)
    view_manager.create(view)
    print 'Global Token: {0}'.format(view_manager.get_token())
    print 'Place this token in the agent.config file'

@db_create_close
def create_groups(conn=None):
    group = Group(
        DefaultGroups.GLOBAL_ADMIN, [Permissions.ADMINISTRATOR],
        views=[DefaultViews.GLOBAL], is_global=True
    )
    group_manager = GroupManager()
    group_results = group_manager.create(group)
    admin_group_id = group_results.generated_ids[0]

    agent_group = Group(
        DefaultGroups.GLOBAL_READ_ONLY, [Permissions.READ],
        views=[DefaultViews.GLOBAL], is_global=True
    )
    agent_group_manager = GroupManager()
    agent_group_results = agent_group_manager.create(agent_group)
    agent_group_id = agent_group_results.generated_ids[0]

    return(admin_group_id, agent_group_id)


@db_create_close
def create_users(admin_group_id, conn=None):
    admin_user = User(
        user_name=DefaultUsers.GLOBAL_ADMIN,
        password=args.admin_password, groups=DefaultGroups.GLOBAL_ADMIN,
        current_view=DefaultViews.GLOBAL,
        default_view=DefaultViews.GLOBAL,
        enabled=True, is_global=True
    )
    user_manager = UserManager(admin_user.user_name)
    user_manager.create(admin_user, [admin_group_id])
    print 'Admin username = %s' % (DefaultUsers.GLOBAL_ADMIN)
    print 'Admin password = %s' % (args.admin_password)


def generate_initial_db_data():
    completed = False
    print 'creating indexes and secondary indexes'
    imported = import_modules_by_regex('_db_init.py')
    print imported
    if not imported:
        print "failed on 1st try {0}".format(imported)
        imported = import_modules_by_regex('_db_init.py')
        print "worked on 4nd try {0}".format(imported)
    print 'creating views, groups, and users'
    create_views()
    admin_group_id, agent_group_id = create_groups()
    create_users(admin_group_id)
    completed = True

    return completed

def start_local_db():
    os.umask(0)
    if not os.path.exists(VFENSE_TMP_PATH):
        os.mkdir(VFENSE_TMP_PATH, 0755)
    if not os.path.exists(RETHINK_CONF):
        subprocess.Popen(
            [
                'ln', '-s',
                RETHINK_SOURCE_CONF,
                RETHINK_CONF
            ],
        )
    if not os.path.exists(RETHINK_VFENSE_PATH):
        os.makedirs(RETHINK_VFENSE_PATH)
        subprocess.Popen(
            [
                'chown', '-R', 'rethinkdb.rethinkdb',
                RETHINK_VFENSE_PATH
            ],
        )

    if not db_connect():
        subprocess.Popen(['service', 'rethinkdb','start'])

    while not db_connect():
        print 'Sleeping until rethink starts'
        sleep(2)

    if db_connect():
        completed = True
        print 'Rethink Initialization and Table creation is now complete'
    else:
        completed = False
        print 'Failed during Rethink startup process'

    return completed

def generate_vuln_data():
    print "Updating CVE's..."
    load_up_all_xml_into_db()
    print "Done Updating CVE's..."
    print "Updating Microsoft Security Bulletin Ids..."
    parse_bulletin_and_updatedb()
    print "Done Updating Microsoft Security Bulletin Ids..."
    print "Updating Ubuntu Security Bulletin Ids...( This can take a couple of minutes )"
    ubuntu_archive_processor(False)
    print "Done Updating Ubuntu Security Bulletin Ids..."
    print "Updating Redhat Security Bulletin Ids...( This can take a couple of minutes )"
    redhat_archive_processor(latest=False)
    print "Done Updating Redhat Security Bulletin Ids..."


def clean_database():
    completed = False
    conn = db_connect()
    if conn:
        subprocess.Popen(['service', 'rethinkdb','stop'])
        sleep(3)
        print 'Rethink stopped successfully\n'
    try:
        if os.path.exists(RETHINK_VFENSE_PATH):
            shutil.rmtree(RETHINK_VFENSE_PATH)
        completed = True
        print 'Rethink instances.d directory removed and cleaned'

    except Exception as e:
        print 'Rethink instances.d directory could not be removed'
        print e
        completed = False

    return completed


if __name__ == '__main__':
    db_initialized = False
    db_started = False
    init_data_completed = False
    create_symlinks()
    create_directories()
    build_nginx_config()
    db_clean = clean_database()
    if db_clean:
        db_started = start_local_db()

    if db_started:
        init_data_completed = generate_initial_db_data()

    if init_data_completed:
        add_local_user()
        db_initialized = True

    if args.cve_data and db_initialized:
        generate_vuln_data()

    if db_initialized:
        print 'vFense environment has been succesfully initialized\n'
        subprocess.Popen(
            [
                'chown', '-R', 'vfense.vfense', VFENSE_BASE_PATH
            ],
        )

    else:
        print 'vFense Failed to initialize'

