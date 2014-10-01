import re

class AgentCommonKeys(object):
    AVAIL_UPDATES = 'available_updates'
    AVAIL_VULN = 'available_vulnerabilities'


class AgentVirtualKeys(object):
    PHYSICAL = 'physical'
    VIRTUAL = 'virtual'


class AgentStatusKeys(object):
    UP = 'up'
    DOWN = 'down'


class Environments(object):
    PRODUCTION = 'Production'


class AgentDefaults(object):
    NEEDS_REBOOT = False
    ENVIRONMENT = Environments.PRODUCTION
    AGENT_STATUS = 'up'
    REBOOTED = True
    VIEWS = ['global']
    TAGS = []
    DISPLAY_NAME = None

def agent_regex():
    return '([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})'
