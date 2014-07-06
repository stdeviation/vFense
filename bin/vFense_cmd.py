#!/usr/bin/env python
import os
import sys
import json
import ConfigParser
import argparse
import cookielib
import requests

API_VERSION = '/api/v1'
SESSION = requests.session()
JAR = cookielib.CookieJar()
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def get_credentials(config=None):
    Config = ConfigParser.ConfigParser()
    file_exists = False
    if not config:
        config = (
            os.path.join(
                os.environ.get('HOME'), '.vFense.config'
            )
        )
    if os.path.exists(config):
        file_exists = True
        Config.read(config)
        username = Config.get('vFense', 'user_name')
        password = Config.get('vFense', 'password')
        url = Config.get('vFense', 'url')
    else:
        username = None
        password = None
        url = None

    return(username, password, url, file_exists)

def authenticate(username, password, url):
    login_url = os.path.join(url, 'login')
    creds = {
        'username': username,
        'password': password
    }
    authenticated = (
        SESSION.post(
            login_url, data=json.dumps(creds),
            verify=False, headers=HEADERS, cookies=JAR
        )
    )
    return authenticated

class vFense(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='vFense command line tool.',
            usage='''vfense <api> [<args>]

The various api base calls.
   users     Search, create, and delete users
   user      Editing and deleting of a user.
''')
        self.username, self.password, self.url, config_exists = (
            get_credentials()
        )
        if config_exists:
            parser.add_argument(
                'api', help='Api to run',
                choices=['users', 'user']
            )
            args = parser.parse_args(sys.argv[1:2])
            if not hasattr(self, args.api):
                print 'Unrecognized api'
                parser.print_help()
                exit(1)
            getattr(self, args.api)()

        else:
            config_file = os.path.join(os.getenv('HOME'), '.vFense.config')
            print 'Missing config {0}'.format(config_file)
            exit(1)

    def user(self):
        self.users_url = os.path.join(self.url, 'api/v1/user')
        parser = argparse.ArgumentParser(
            description='users api calls')
        parser.add_argument(
            'command', help='commands available for users',
            choices=['get', 'edit', 'delete', 'add', 'remove']
        )
        parser.add_argument(
            'user_name', help='name of the user'
        )
        args = parser.parse_args(sys.argv[2:4])
        if args.command == 'get':
            self.user_get(args.user_name)

        elif args.command == 'delete':
            self.user_delete(args.user_name)

        elif args.command == 'edit':
            self.user_edit(args.user_name)


    def user_get(self, user_name):
        self.user_url = os.path.join(self.url, 'api/v1/user', user_name)
        vfense = authenticate(self.username, self.password, self.url)
        if vfense.ok:
            data = (
                SESSION.get(
                    self.user_url, verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            content = json.loads(data.content)
            print json.dumps(content['data'], indent=4)


    def user_edit(self, user_name):
        msg = 'Edit the attributes of this user {0}'.format(user_name)
        parser = argparse.ArgumentParser(description=msg)
        self.user_url = os.path.join(self.url, 'api/v1/user', user_name)
        vfense = authenticate(self.username, self.password, self.url)
        if vfense.ok:
            parser.add_argument(
                '--password', dest='password', type=str,
                help='The current password of the user.', default=None
            )
            parser.add_argument(
                '--new_password', dest='new_password', type=str,
                help='The new password of the user.', default=None
            )
            parser.add_argument(
                '--fullname', dest='fullname', type=str,
                help='Edit the full name of the user.', default=None
            )
            parser.add_argument(
                '--email', dest='email', type=str,
                help='Edit the email of the user.', default=None
            )
            parser.add_argument(
                '--current_view', dest='current_view', type=str,
                help='Change the current view of the user.', default=None
            )
            parser.add_argument(
                '--default_view', dest='default_view', type=str,
                help='Change the default view of the user.', default=None
            )
            parser.add_argument(
                '--enabled', dest='enabled', type=str,
                help='Enable or disable a user.', default=None,
                choices=['toggle']
            )
            args = parser.parse_args(sys.argv[4:])
            pay_load = vars(args)
            data = (
                SESSION.put(
                    self.user_url, data=json.dumps(pay_load), verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            content = json.loads(data.content)
            print json.dumps(content['data'], indent=4)


    def user_delete(self, user_name):
        self.user_url = os.path.join(self.url, 'api/v1/user', user_name)
        vfense = authenticate(self.username, self.password, self.url)
        if vfense.ok:
            data = (
                SESSION.delete(
                    self.user_url, verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            content = json.loads(data.content)
            print json.dumps(content, indent=4)


    def users(self):
        self.users_url = os.path.join(self.url, 'api/v1/users')
        parser = argparse.ArgumentParser(
            description='users api calls'
        )
        parser.add_argument(
            'command', help='commands available for users',
            choices=['search', 'create', 'delete']
        )
        args = parser.parse_args(sys.argv[2:3])
        if args.command == 'search':
            self.users_search()


    def user_create(self):
        parser = argparse.ArgumentParser(
            description='Create a new user'
        )
        vfense = authenticate(self.username, self.password, self.url)
        if vfense.ok:
            parser.add_argument(
                '--user_name', dest='user_name', type=str,
                help='The name of the user, you are creating.'
            )
            parser.add_argument(
                '--password', dest='password', type=str,
                help='''The password of the user you are createing.
            The password must contain the following: 1 Special characater,
            1 Uppercase, 1 Lowercase, 1 Number, and a total of 8 characters'''
            )
            parser.add_argument(
                '--full_name', dest='full_name', type=str,
                help='The full name of the user, you are creating.'
            )
            parser.add_argument(
                '--email', dest='email', type=str,
                help='The email address of the user, you are creating.'
            )
            parser.add_argument(
                '--enabled', dest='enabled', type=bool, action='store_true',
                help='Create the user as enabled, the default is disabled',
                default=False
            )
            parser.add_argument(
                '--is_global', dest='is_global', action='store_true',
                help='The email address of the user, you are creating.',
                default=False
            )
            parser.add_argument(
                '--group_ids', dest='group_ids', action='append',
                help='The group ids, this user will be a part of.'
            )
            parser.add_argument(
                '--view_context', dest='view_context', type=str,
                help='''The view this user is being created in.
            The default is to use the view of the currently logged in user.'''
            )
            args = parser.parse_args(sys.argv[3:])
            pay_load = vars(args)
            data = (
                SESSION.post(
                    self.user_url, data=json.dumps(pay_load), verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            content = json.loads(data.content)
            print json.dumps(content, indent=4)

    def users_search(self):

        parser = argparse.ArgumentParser(
            description='Search for users.'
        )
        parser.add_argument(
            '--count', dest='count', default=30, type=int,
            help='The max amount of results to return with this query.'
        )
        parser.add_argument(
            '--offset', dest='offset', default=0, type=int,
            help='From where the search begins.'
        )
        parser.add_argument(
            '--sort', dest='sort', default='asc', type=str,
            choices=['asc', 'desc'], help='From where the search begins.'
        )
        parser.add_argument(
            '--sort_by', dest='sort_by', default='view_name', type=str,
            choices=['view_name'], help='The key that will be used to sort by.'
        )
        args = parser.parse_args(sys.argv[3:])
        pay_load = vars(args)
        vfense = authenticate(self.username, self.password, self.url)
        if vfense.ok:
            data = (
                SESSION.get(
                    self.users_url, params=pay_load, verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            content = json.loads(data.content)
            print json.dumps(content['data'], indent=4)


if __name__ == '__main__':
    vFense()
