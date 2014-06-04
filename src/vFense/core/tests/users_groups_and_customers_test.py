import unittest

from vFense.core.group import Group
from vFense.core.group._db_model import (
    GroupKeys
)
from vFense.core.group._db import (
    fetch_group_by_name
)
from vFense.core.group.manager import GroupManager
from vFense.core.view import View
from vFense.core.view.manager import ViewManager
from vFense.core.user import User
from vFense.core.user.manager import UserManager
from vFense.errorz.status_codes import (
    ViewCodes, GroupCodes, UserCodes
)
from vFense.errorz._constants import ApiResultKeys
from vFense.core.permissions._constants import Permissions
from vFense.core.group._constants import DefaultGroups
from vFense.core.view._constants import DefaultViews
from vFense.core.user._constants import DefaultUsers

class UsersGroupsAndViewsTests(unittest.TestCase):

    def test_a_create_view(self):
        view = View(
            DefaultViews.GLOBAL,
            package_download_url='https://10.0.0.15/packages/'
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_b_create_group(self):
        group = Group(
            DefaultGroups.GLOBAL_ADMIN, [Permissions.ADMINISTRATOR],
            [DefaultViews.GLOBAL], True
        )
        manager = GroupManager()
        results = manager.create(group)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


    def test_c_create_user(self):
        global_group_id = (
            fetch_group_by_name(
                DefaultGroups.GLOBAL_ADMIN, DefaultViews.GLOBAL
            ).get(GroupKeys.GroupId)
        )
        user = User(
            DefaultUsers.GLOBAL_ADMIN,
            'vFense#123', 'Global Administrator',
            current_view=DefaultViews.GLOBAL,
            default_view=DefaultViews.GLOBAL,
            enabled=True, is_global=True
        )
        manager = UserManager(user.name)
        results = manager.create(user, [global_group_id])
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserCreated)

"""

    def test_h_edit_user(self):
        props = {
            UserKeys.FullName: 'Ninja Unit Tester 1'
        }
        results = edit_user_properties('test1', **props)
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_i_edit_password(self):
        results = change_password('test1', 'T35t#123', 'T35t#1234')
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_j_add_user_to_group(self):
        group_test_id = (
            get_group_by_name('Tester 4 life Part 2', 'test').get(GroupKeys.GroupId)
        )
        results = add_user_to_groups('test2', 'test', [group_test_id])
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)
    def test_k_remove_groups_from_user(self):
        group_test_id = (
            get_group_by_name('Tester 4 life Part 1', 'test').get(GroupKeys.GroupId)
        )
        results = remove_groups_from_user('test3', [group_test_id])
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_l_remove_views_from_user(self):
        results = remove_views_from_user('test3', ['test'])
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)


    def test_m_remove_user(self):
        results = remove_user('test3')
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_n_remove_users(self):
        results = remove_users(['test1', 'test2'])
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_o_remove_groups1(self):
        group_test_id = (
            get_group_by_name('Tester 4 life Part 1', 'test').get(GroupKeys.GroupId)
        )
        results = remove_group(group_test_id)
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_p_remove_groups2(self):
        group_test_id = (
            get_group_by_name('Tester 4 life Part 2', 'test').get(GroupKeys.GroupId)
        )
        results = remove_group(group_test_id)
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_q_remove_view1(self):
        results = remove_view('test')
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)


"""

def main():
    unittest.main()

if __name__ == '__main__':
    main()
