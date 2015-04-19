import sys
import argparse
import ConfigParser
from _magic import *
from vFense._constants import (
    VFENSE_LOGGING_CONFIG, VFENSE_CONFIG
)
from vFense.core.logger.logger import vFenseLogger

vfense_logger = vFenseLogger()
vfense_logger.create_config()

import logging, logging.config

from vFense.utils.common import import_modules_by_regex
import nginx_config_creator as ncc
from vFense.utils.supported_platforms import (
    DEBIAN_DISTROS, get_distro
)
from vFense.utils.security import generate_pass, check_password
from vFense.utils.ssl_initialize import generate_generic_certs
from vFense.utils.common import pick_valid_ip_address
from vFense.db.client import r, db_create_close

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
from vFense.plugins.vuln.ubuntu.parser import begin_usn_home_page_processing
from vFense.plugins.vuln.redhat.parser import begin_redhat_archive_processing

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

Config = ConfigParser.ConfigParser()
Config.read(VFENSE_CONFIG)


parser = argparse.ArgumentParser(description='Initialize vFense Options')
parser.add_argument(
    '--dnsname', dest='dns_name', default=None,
    help='Pass the DNS Name of the patching Server'
)
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


if args.dns_name:
    url = 'https://%s/packages/' % (args.dns_name)
    nginx_server_name = args.dns_name
else:
    url = 'https://%s/packages/' % (args.ip_address)
    nginx_server_name = args.ip_address

def build_nginx_config():
    generate_generic_certs()
    ncc.nginx_config_builder(nginx_server_name)

@db_create_close
def create_views(conn=None):
    view = View(
        view_name=DefaultViews.GLOBAL,
        server_queue_ttl=Config.get('vFense', 'server_queue_ttl'),
        package_download_url_base=Config.get('vFense', 'packages_url')
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

@db_create_close
def generate_initial_db_data(conn=None):
    completed = False
    if conn:
        r.db_create('vFense').run(conn)
        conn.close()
        print 'creating indexes and secondary indexes'
        import_modules_by_regex('_db_init.py')
        print 'creating views, groups, and users'
        create_views()
        admin_group_id, agent_group_id = create_groups()
        create_users(admin_group_id)
        completed = True

    return completed

def generate_vuln_data():
    print "Updating CVE's..."
    load_up_all_xml_into_db()
    print "Done Updating CVE's..."
    print "Updating Microsoft Security Bulletin Ids..."
    parse_bulletin_and_updatedb()
    print "Done Updating Microsoft Security Bulletin Ids..."
    print "Updating Ubuntu Security Bulletin Ids...( This can take a couple of minutes )"
    begin_usn_home_page_processing(full_parse=True)
    print "Done Updating Ubuntu Security Bulletin Ids..."
    print "Updating Redhat Security Bulletin Ids...( This can take a couple of minutes )"
    begin_redhat_archive_processing(latest=False)
    print "Done Updating Redhat Security Bulletin Ids..."


if __name__ == '__main__':
    db_initialized = False
    db_started = False
    init_data_completed = False
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

    else:
        print 'vFense Failed to initialize'
