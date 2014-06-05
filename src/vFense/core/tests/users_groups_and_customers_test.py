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

    def test_a_create_view1(self):
        view = View(
            DefaultViews.GLOBAL,
            package_download_url='https://10.0.0.15/packages/'
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_a_create_view2(self):
        view = View(
            'Test View 1',
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_a_create_view3(self):
        view = View(
            'Test View 2',
            parent='Test View 1'
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_b_create_group1(self):
        group = Group(
            DefaultGroups.GLOBAL_ADMIN, [Permissions.ADMINISTRATOR],
            [DefaultViews.GLOBAL], True
        )
        manager = GroupManager()
        results = manager.create(group)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


    def test_b_create_group2(self):
        group = Group(
            'Tester 1', [Permissions.INSTALL, Permissions.UNINSTALL],
            ['Test View 1', 'Test View 2']
        )
        manager = GroupManager()
        results = manager.create(group)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)

    def test_b_create_group3(self):
        group = Group(
            'Tester 2', [Permissions.ADMINISTRATOR],
            ['Test View 2']
        )
        manager = GroupManager()
        results = manager.create(group)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


    def test_c_create_user1(self):
        global_group_id = (
            fetch_group_by_name(
                DefaultGroups.GLOBAL_ADMIN, DefaultViews.GLOBAL
            ).get(GroupKeys.GroupId)
        )
        print global_group_id
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

    def test_c_create_user2(self):
        group_id_1 = (
            fetch_group_by_name(
                'Tester 1', 'Test View 1'
            ).get(GroupKeys.GroupId)
        )
        print group_id_1
        user = User(
            'tester1',
            'vFense#123', 'test user 1',
            current_view='Test View 1',
            default_view='Test View 1',
            enabled=True, is_global=False
        )
        manager = UserManager(user.name)
        results = manager.create(user, [group_id_1])
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserCreated)


    def test_d_add_to_view1(self):
        manager = UserManager('tester1')
        results = manager.add_to_views(['Test View 2'])
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewsAddedToUser)


    def test_e_add_to_group1(self):
        group_id = (
            fetch_group_by_name(
                'Tester 2', 'Test View 2'
            ).get(GroupKeys.GroupId)
        )
        print group_id
        manager = UserManager('tester1')
        results = manager.add_to_groups([group_id])
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupsAddedToUser)

    def test_f_change_full_name(self):
        user = User(
            DefaultUsers.GLOBAL_ADMIN,
            full_name="Shaolin Administrator"
        )
        manager = UserManager(user.name)
        results = manager.change_full_name(user)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserUpdated)

    def test_g_change_email(self):
        user = User(
            DefaultUsers.GLOBAL_ADMIN,
            email="shaolin@foo.com"
        )
        manager = UserManager(user.name)
        results = manager.change_email(user)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserUpdated)

    def test_h_change_password(self):
        password = 'vFense#123'
        new_password = 'vFense#12345'
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.change_password(password, new_password)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.PasswordChanged)

    def test_i_reset_password(self):
        password = 'vFense#123'
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.reset_password(password)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.PasswordChanged)
"""

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
