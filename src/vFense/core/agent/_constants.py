class AgentCommonKeys(object):
    AVAIL_UPDATES = 'available_updates'
    AVAIL_VULN = 'available_vulnerabilities'


class AgentVirtualKeys(object):
    PHYSICAL = 'physical'
    VIRTUAL = 'virtual'


class AgentStatusKeys(object):
    UP = 'up'
    DOWN = 'down'


class ProductionLevels(object):
    PRODUCTION = 'production'


class AgentDefaults(object):
    NEEDS_REBOOT = False
    PRODUCTION_LEVEL = ProductionLevels.PRODUCTION
    AGENT_STATUS = 'up'
    REBOOTED = True
    VIEWS = ['global']
    DISPLAY_NAME = None
