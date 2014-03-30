import unittest

from vFense.core._constants import *
from vFense.core.user._constants import *
from vFense.core.user.users import *
from vFense.core.group.groups import *
from vFense.core.group._constants import *
from vFense.core.customer.customers import *
from vFense.core.customer._constants import *
from vFense.core.permissions._constants import *
from vFense.errorz._constants import *

class UsersGroupsAndCustomersTests(unittest.TestCase):

    def test_create_customer(self):
        results = (
            create_customer(
                'test',
                http_application_url_location='https://10.0.0.1/packages',
                init=True
            )
        )
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_create_group(self):
        results = (
            create_group(
                'Tester 4 life', 'test', [Permissions.ADMINISTRATOR]
            )
        )
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    def test_create_user(self):
        group_test_id = (
            get_group_by_name('Tester 4 life', 'test').get(GroupKeys.GroupId)
        )
        results = create_user(
            'test1', 'Unit Test 1', 'T35t#123',
            [group_test_id], 'test', 'test@test.org', 'yes',
            'tester', '/test', 'TEST'
        ) 
        http_status_code = results.get(ApiResultKeys.HTTP_STATUS_CODE)
        self.failUnless(http_status_code == 200)

    #def testTwo(self):
    #    self.failIf(IsOdd(2))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
