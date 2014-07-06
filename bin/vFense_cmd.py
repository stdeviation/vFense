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
    if not config:
        config = (
            os.path.join(
                os.environ.get('HOME'), '.vFense.config'
            )
        )
    if os.path.exists(config):
        Config.read(config)
        username = Config.get('vFense', 'user_name')
        password = Config.get('vFense', 'password')
        url = Config.get('vFense', 'url')
    else:
        username = None
        password = None
        url = None

    return(username, password, url)

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
        parser.add_argument(
            'api', help='Api to run',
            choices=['users', 'user']
        )
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.api):
            print 'Unrecognized api'
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.api)()

    def users(self):
        parser = argparse.ArgumentParser(
            description='users api calls')
        parser.add_argument(
            'command', help='commands available for users',
            choices=['search', 'create', 'delete']
        )
        args = parser.parse_args(sys.argv[2:3])
        print ' api call %s' % args.command
        if args.command == 'search':
            self.users_search()

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
        username, password, url = get_credentials()
        users_url = os.path.join(url, 'api/v1/users')
        vfense = authenticate(username, password, url)
        if vfense.ok:
            data = (
                SESSION.get(
                    users_url, params=pay_load, verify=False,
                    headers=HEADERS, cookies=JAR
                )
            )
            print data.content


if __name__ == '__main__':
    vFense()
