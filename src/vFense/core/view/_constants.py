from vFense.core._constants import CPUThrottleValues


class DefaultViews():
    DEFAULT = 'default'


class ViewDefaults():
    PARENT = None
    ANCESTORS = []
    CHILDREN = []
    NET_THROTTLE = 0
    CPU_THROTTLE = CPUThrottleValues.NORMAL
    SERVER_QUEUE_TTL = 10  #minutes
    AGENT_QUEUE_TTL = 10  #minutes
