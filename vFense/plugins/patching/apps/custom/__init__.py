from vFense.plugins.patching import Apps
from vFense.plugins.patching._db_model import CustomAppsKey
from vFense.plugins.patching._constants import AppDefaults


class CustomApps(Apps):
    def __init__(self, vfense_app_id=None, cli_options=None, **kwargs):
        """
        Kwargs:
            vfense_app_id (str): The primary key of this application
            cli_options (str): The arguments that need to be passed with
                the install of this application
        """
        super(Apps, self).__init__(**kwargs)

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.vfense_app_id:
            self.vfense_app_id = ''

        if not self.hidden:
            self.hidden = AppDefaults.hidden()

        if not self.reboot_required:
            self.reboot_required= AppDefaults.reboot_required()

        if not self.files_download_status:
            self.files_download_status = AppDefaults.download_status()

        if not self.vulnerability_categories:
            self.vulnerability_categories = AppDefaults.vuln_categories()

        if not self.vulnerability_id:
            self.vulnerability_id = AppDefaults.vuln_id()

        if not self.cve_ids:
            self.cve_ids = AppDefaults.cve_ids()


    def to_dict_apps(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        data = super(Apps, self).to_dict_apps()
        data[CustomAppsKey.CliOptions] = self.cli_options
        data[CustomAppsKey.vFenseAppId] = self.vfense_app_id

        return data
