from vFense.core.agent._constants import Environments

class TagDefaults(object):
    ENVIRONMENT = Environments.PRODUCTION
    IS_GLOBAL = False
    VIEW_NAME = 'global'
    AGENTS = []

def tag_id():
    return '[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}'

def tag_regex():
    return '({0})'.format(tag_id())
