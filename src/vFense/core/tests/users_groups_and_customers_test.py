import unittest
from json import dumps

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
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_a_create_view2(self):
        view = View(
            'Test View 1',
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_a_create_view3(self):
        view = View(
            'Test View 2',
            parent='Test View 1'
        )
        manager = ViewManager(view.name)
        results = manager.create(view)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewCreated)


    def test_b_create_group1(self):
        group = Group(
            DefaultGroups.GLOBAL_ADMIN, [Permissions.ADMINISTRATOR],
            [DefaultViews.GLOBAL], True
        )
        manager = GroupManager()
        results = manager.create(group)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


    def test_b_create_group2(self):
        group = Group(
            'Tester 1', [Permissions.INSTALL, Permissions.UNINSTALL],
            ['Test View 1', 'Test View 2']
        )
        manager = GroupManager()
        results = manager.create(group)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)

    def test_b_create_group3(self):
        group = Group(
            'Tester 2', [Permissions.ADMINISTRATOR],
            ['Test View 2']
        )
        manager = GroupManager()
        results = manager.create(group)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


    def test_c_create_user1(self):
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
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserCreated)

    def test_c_create_user2(self):
        group_id_1 = (
            fetch_group_by_name(
                'Tester 1', 'Test View 1'
            ).get(GroupKeys.GroupId)
        )
        user = User(
            'tester1',
            'vFense#123', 'test user 1',
            current_view='Test View 1',
            default_view='Test View 1',
            enabled=True, is_global=False
        )
        manager = UserManager(user.name)
        results = manager.create(user, [group_id_1])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserCreated)


    def test_d_add_to_view1(self):
        manager = UserManager('tester1')
        results = manager.add_to_views(['Test View 2'])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewsAddedToUser)


    def test_e_add_to_group1(self):
        group_id = (
            fetch_group_by_name(
                'Tester 2', 'Test View 2'
            ).get(GroupKeys.GroupId)
        )
        manager = UserManager('tester1')
        results = manager.add_to_groups([group_id])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupsAddedToUser)

    def test_f_remove_from_group1(self):
        group_id = (
            fetch_group_by_name(
                'Tester 2', 'Test View 2'
            ).get(GroupKeys.GroupId)
        )
        manager = UserManager('tester1')
        results = manager.remove_from_groups([group_id])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupsRemovedFromUser)


    def test_g_remove_from_view1(self):
        manager = UserManager('tester1')
        results = manager.remove_from_views(['Test View 2'])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewsRemovedFromUser)


    def test_h_add_to_group1(self):
        group_id = (
            fetch_group_by_name(
                'Tester 2', 'Test View 2'
            ).get(GroupKeys.GroupId)
        )
        manager = UserManager('tester1')
        results = manager.add_to_groups([group_id])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupsAddedToUser)


    def test_i_add_to_view1(self):
        manager = UserManager('tester1')
        results = manager.add_to_views(['Test View 2'])
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == ViewCodes.ViewsAddedToUser)


    def test_j_change_full_name(self):
        user = User(
            DefaultUsers.GLOBAL_ADMIN,
            full_name="Shaolin Administrator"
        )
        manager = UserManager(user.name)
        results = manager.change_full_name(user)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserUpdated)

    def test_k_change_email(self):
        user = User(
            DefaultUsers.GLOBAL_ADMIN,
            email="shaolin@foo.com"
        )
        manager = UserManager(user.name)
        results = manager.change_email(user)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserUpdated)


    def test_l_change_password(self):
        password = 'vFense#123'
        new_password = 'vFense#12345'
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.change_password(password, new_password)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.PasswordChanged)


    def test_m_reset_password(self):
        password = 'vFense#123'
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.reset_password(password)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.PasswordChanged)

    def test_n_remove_global_admin_from_groups1(self):
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.remove_from_groups(remove_admin=True)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupsRemovedFromUser)

    def test_o_remove1(self):
        manager = UserManager(DefaultUsers.GLOBAL_ADMIN)
        results = manager.remove()
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserDeleted)

    def test_o_remove2(self):
        manager = UserManager('tester1')
        results = manager.remove()
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == UserCodes.UserDeleted)

    def test_p_remove_group1(self):
        group_id = (
            fetch_group_by_name(
                DefaultGroups.GLOBAL_ADMIN, DefaultViews.GLOBAL
            ).get(GroupKeys.GroupId)
        )
        manager = GroupManager(group_id)
        results = manager.remove()
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)

    def test_p_remove_group2(self):
        group_id = (
            fetch_group_by_name(
               'Tester 1', 'Test View 1'
            ).get(GroupKeys.GroupId)
        )
        manager = GroupManager(group_id)
        results = manager.remove()
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)

    def test_p_remove_group3(self):
        group_id = (
            fetch_group_by_name(
               'Tester 2', 'Test View 1'
            ).get(GroupKeys.GroupId)
        )
        manager = GroupManager(group_id)
        results = manager.remove()
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == GroupCodes.GroupCreated)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
