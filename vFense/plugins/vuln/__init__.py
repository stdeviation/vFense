from vFense.plugins.vuln import VulnDefaults


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
            self.cve_ids = VulnDefaults.CVE_IDS

        if not self.os_strings:
            self.os_strings= VulnDefaults.OS_STRINGS

        if not self.support_url:
            self.support_url= VulnDefaults.SUPPORT_URL

        if not self.details:
            self.details= VulnDefaults.DETAILS

        if not self.apps:
            self.apps= VulnDefaults.APPS

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
                        FilesKey.FileName: self.file_name,
                        CommonKeys.REASON: (
                            '{0} not a valid file name'
                            .format(self.file_name)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.file_size:
            if not int(self.file_size):
                invalid_fields.append(
                    {
                        FilesKey.FileSize: self.file_size,
                        CommonKeys.REASON: (
                            '{0} not a valid file size'
                            .format(self.file_size)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.file_hash:
            if len(self.file_hash) <= 1:
                invalid_fields.append(
                    {
                        FilesKey.FileHash: self.file_hash,
                        CommonKeys.REASON: (
                            '{0} not a valid hash'
                            .format(self.file_hash)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.app_ids:
            if not isinstance(self.app_ids, list):
                invalid_fields.append(
                    {
                        FilesKey.AppIds: self.app_ids,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.app_ids)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.agent_ids:
            if not isinstance(self.agent_ids, list):
                invalid_fields.append(
                    {
                        FilesKey.AgentIds: self.agent_ids,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.agent_ids)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.download_url:
            if len(self.download_url) <= 1:
                invalid_fields.append(
                    {
                        FilesKey.FileUri: self.download_url,
                        CommonKeys.REASON: (
                            '{0} not a valid url'
                            .format(self.download_url)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
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
            FilesKey.FileName: self.file_name,
            FilesKey.AppIds: self.app_ids,
            FilesKey.AgentIds: self.agent_ids,
            FilesKey.FileUri: self.download_url,
            FilesKey.FileHash: self.file_hash,
            FilesKey.FileSize: self.file_size,
        }

    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}
