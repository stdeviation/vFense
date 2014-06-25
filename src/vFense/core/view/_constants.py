from vFense.core._constants import CPUThrottleValues


class DefaultViews():
    GLOBAL = 'global'


class ViewDefaults():
    PARENT = None
    ANCESTORS = []
    CHILDREN = []
    USERS = []
    NET_THROTTLE = 0
    CPU_THROTTLE = CPUThrottleValues.NORMAL
    SERVER_QUEUE_TTL = 10  #minutes
    AGENT_QUEUE_TTL = 10  #minutes
    TOKEN = None
    PREVIOUS_TOKENS = []
