
from vFense.core.permissions import *
from vFense.core.user import *
from vFense.core.groups import *
from vFense.core.user.users import get_user

def get_all_permissions_for_user
def check_permission(permission):
    def wrapper(fn):
        def wrapped(*args):
            granted = False
            tornado_handler = args[0]
            username = tornado_handler.get_current_user()
            valid_user = get_user(username)

