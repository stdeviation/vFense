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
    DISPLAY_NAME = None
