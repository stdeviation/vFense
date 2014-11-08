from time import time

class CommonKeys():
    YES = 'yes'
    NO = 'no'
    TOGGLE = 'toggle'
    TRUE = 'true'
    FALSE = 'false'
    COUNT = 'count'
    DETAILS = 'details'
    GROUP = 'group'
    REDUCTION = 'reduction'
    USERNAME = 'username'
    PASSWORD = 'password'
    USER = 'user'
    URI = 'uri'
    METHOD = 'method'
    RESPONSE_URI = 'response_uri'
    REQUEST_METHOD = 'request_method'
    OPERATION = 'operation'
    REASON = 'reason'


class DefaultStringLength():
    VIEW_NAME = 36
    GROUP_NAME = 36
    USER_NAME = 24


class RegexPattern():
    USERNAME = (
        r'(^[A-Za-z0-9_-]{1,%d}$)' %
        (DefaultStringLength.USER_NAME)
    )
    VIEW_NAME = (
        r'(^(?:[A-Za-z0-9_-](?!\s+")|\s(?!\s*")){1,%d}$)' %
        (DefaultStringLength.VIEW_NAME)
    )
    GROUP_NAME = (
        r'(^(?:[A-Za-z0-9_-](?!\s+")|\s(?!\s*")){1,%d}$)' %
        (DefaultStringLength.GROUP_NAME)
    )

class HTTPMethods():
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'


class CPUThrottleValues():
    IDLE = 'idle'
    BELOW_NORMAL = 'below_normal'
    NORMAL = 'normal'
    ABOVE_NORMAL = 'above_normal'
    HIGH = 'high'
    VALID_VALUES = (IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH)


class RebootValues():
    NONE = 'none' #Do not reboot
    NEEDED = 'needed' #Reboot only if the system is asking for a reboot
    FORCE = 'force'   #Force the reboot
    VALID_VALUES = (NONE, NEEDED, FORCE)


class SortValues():
    ASC = 'asc'
    DESC = 'desc'


class SortLogic():
    EQ = '=='
    GE = '>='
    LE = '<='
    GT = '>'
    LT = '<'
    NE = '!='
    OR = '|'
    AND = '&'
    VALID_VALUES = (EQ, GE, LE, GT, LT, NE)


class DefaultQueryValues():
    COUNT = 30
    OFFSET = 0
    SORT = SortValues.ASC


class Time(object):
    @staticmethod
    def now():
        return(int(time()))

    @staticmethod
    def begining_of_time():
        return 0
