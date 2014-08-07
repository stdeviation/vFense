from vFense.core._constants import CommonKeys
from vFense.core._db_constants import DbTime
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes
from vFense.plugins.vuln._constants import VulnDefaults
from vFense.plugins.vuln._db_model import VulnerabilityKeys


class Vulnerability(object):
    """Used to represent an instance of an app."""

    def __init__(self, vulnerability_id=None, date_posted=None,
                 details=None, cve_ids=None, support_url=None,
                 os_strings=None, apps=None):
        """
        Kwargs:
        """
        self.vulnerability_id = vulnerability_id
        self.date_posted = date_posted
        self.details = details
        self.cve_ids = cve_ids
        self.support_url = support_url
        self.os_strings = os_strings
        self.apps = apps

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.cve_ids:
            self.cve_ids = list()

        if not self.os_strings:
            self.os_strings = list()

        if not self.support_url:
            self.support_url = VulnDefaults.SUPPORT_URL

        if not self.details:
            self.details = VulnDefaults.DETAILS

        if not self.apps:
            self.apps = list()

        if not self.date_posted:
            self.date_posted = 0

    def get_invalid_fields(self):
        """Check the app for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.cve_ids:
            if not isinstance(self.cve_ids, list):
                invalid_fields.append(
                    {
                        VulnerabilityKeys.CveIds: self.cve_ids,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.cve_ids)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.apps:
            if not isinstance(self.apps, list):
                invalid_fields.append(
                    {
                        VulnerabilityKeys.Apps: self.apps,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.apps)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.os_strings:
            if not isinstance(self.os_strings, list):
                invalid_fields.append(
                    {
                        VulnerabilityKeys.OsStrings: self.os_strings,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.os_strings)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.date_posted:
            if (not isinstance(self.date_posted, float) and
                    not isinstance(self.date_posted, int)):
                invalid_fields.append(
                    {
                        VulnerabilityKeys.DatePosted: self.date_posted,
                        CommonKeys.REASON: (
                            '{0} not a valid date, float or int only'
                            .format(type(self.date_posted))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            VulnerabilityKeys.VulnerabilityId: self.vulnerability_id,
            VulnerabilityKeys.Apps: self.apps,
            VulnerabilityKeys.DatePosted: self.date_posted,
            VulnerabilityKeys.CveIds: self.cve_ids,
            VulnerabilityKeys.OsStrings: self.os_strings,
            VulnerabilityKeys.Details: self.details,
            VulnerabilityKeys.SupportUrl: self.support_url,
        }

    def to_dict_db(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        data = {
            VulnerabilityKeys.DatePosted: (
                DbTime.epoch_time_to_db_time(self.date_posted)
            ),
        }

        return dict(self.to_dict().items() + data.items())


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}
