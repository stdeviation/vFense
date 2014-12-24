from vFense import Base
from vFense.core._constants import CommonKeys
from vFense.core._db_constants import DbTime
from vFense.core.results import ApiResultKeys
from vFense.plugins.patching._constants import (
    AppDefaults, RebootValues, HiddenValues, UninstallableValues,
    CommonSeverityKeys, FileDefaults, AppStatuses, CommonAppKeys,
    CommonFileKeys
)
from vFense.plugins.patching._db_model import (
    DbCommonAppKeys, FilesKey, DbCommonAppPerAgentKeys
)

from vFense.plugins.patching.status_codes import (
    PackageCodes
)

from vFense.plugins.patching.utils import (
    build_app_id, build_agent_app_id, get_proper_severity
)

class Apps(Base):
    """Used to represent an instance of an app."""

    def __init__(self, name=None, version=None,
                 arch=None, app_id=None, kb=None, support_url=None,
                 vendor_severity=None, vfense_severity=None,
                 os_code=None, os_string=None, vendor_name=None,
                 description=None, cli_options=None, release_date=None,
                 reboot_required=None, hidden=None, uninstallable=None,
                 repo=None, files_download_status=None, vulnerability_id=None,
                 id=None, update=None,install_date=None, status=None,
                 agent_id=None, dependencies=None, last_modified_time=None,
                 vulnerability_categories=None, cve_ids=None, views=None,
                 **kwargs):
        """
        Kwargs:
            name (str): Name of the application.
            version (str): Current version of the application.
            arch (int): 64 or 32.
            app_id (str): The primary key of this application.
            support_url (str): The vendor supplied url.
            vendor_severity (str): This is the vendor supplied severity.
            vfense_severity (str): Optional, Recommended, or Critical
            os_code (str): windows, linux, or darwin
            os_string (str): CentOS 6.5, Ubuntu 12.0.4, etc...
            vendor_name (str): The vendor, this application belongs too.
            description (str): The description of this application.
            cli_options (str): Options to be passed while installing this
                application.
            release_date (float): The Unix timestamp aka epoch time.
            reboot_required (str): possible, required, none
            hidden (str): no or yes.
            uninstallable (str): yes or no.
            repo (str): repository this application belongs too.
            files_download_status (int): The integer status code that represents
                if this application has been downloaded successfully.
            vulnerability_id (str): The vulnerability identifier assigned
                by the respective vendor.
            vulnerability_categories (list): List of vulnerabilty categories.
            cve_ids (list): List of cve ids that reference this application.
            id (str): The primary key of this application.
            update (int): The integer status code that represents if this
                application is a new install or an update.
            install_date (float): The Unix timestamp aka epoch time.
            status (str): installed or available or pending.
            agent_id (str): The id of the agent that requires this application.
            last_modified_time (float): The Unix timestamp aka epoch time.
            views (list): List of views, this application is associated with.

        """
        super(Apps, self).__init__(**kwargs)
        self.name = name
        self.version = version
        self.arch = arch
        self.app_id = app_id
        self.kb = kb
        self.support_url = support_url
        self.vendor_severity = vendor_severity
        self.vfense_severity = vfense_severity
        self.os_code = os_code
        self.os_string = os_string
        self.vendor_name = vendor_name
        self.description = description
        self.cli_options = cli_options
        self.release_date = release_date
        self.reboot_required = reboot_required
        self.hidden = hidden
        self.files_download_status = files_download_status
        self.uninstallable = uninstallable
        self.repo = repo
        self.vulnerability_id = vulnerability_id
        self.vulnerability_categories = vulnerability_categories
        self.cve_ids = cve_ids
        self.install_date = install_date
        self.id = id
        self.update = update
        self.status = status
        self.agent_id = agent_id
        self.dependencies = dependencies
        self.last_modified_time = last_modified_time
        self.views = views

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.app_id:
            self.app_id = build_app_id(self.name, self.version)

        if not self.hidden:
            self.hidden = AppDefaults.hidden()

        if not self.reboot_required:
            self.reboot_required= AppDefaults.reboot_required()

        if not self.files_download_status:
            self.files_download_status = AppDefaults.download_status()

        if not self.vfense_severity:
            self.vfense_severity = get_proper_severity(self.vendor_severity)

        if not self.vulnerability_categories:
            self.vulnerability_categories = AppDefaults.vuln_categories()

        if not self.vulnerability_id:
            self.vulnerability_id = AppDefaults.vuln_id()

        if not self.cve_ids:
            self.cve_ids = AppDefaults.cve_ids()

    def fill_in_app_per_agent_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.dependencies:
            self.dependencies = AppDefaults.dependencies()

        if not self.id:
            self.id = build_agent_app_id(self.agent_id, self.app_id)

        if not self.update:
            self.update = AppDefaults.update()

        if not self.views:
            self.views = AppDefaults.views()

        if not self.install_date:
            self.install_date = 0


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

        if self.name:
            if len(self.name) < 1:
                invalid_fields.append(
                    {
                        DbCommonAppKeys.Name: self.name,
                        CommonKeys.REASON: (
                            '{0} not a valid application name'
                            .format(self.name)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.version:
            if len(self.version) < 1:
                invalid_fields.append(
                    {
                        DbCommonAppKeys.Version: self.version,
                        CommonKeys.REASON: (
                            '{0} not a valid application version'
                            .format(self.version)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.reboot_required:
            if (self.reboot_required not
                    in RebootValues.get_values()):
                invalid_fields.append(
                    {
                        DbCommonAppKeys.RebootRequired: self.reboot_required,
                        CommonKeys.REASON: (
                            '{0} not a valid reboot value'
                            .format(self.reboot_required)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )


        if self.hidden:
            if (self.hidden not
                    in HiddenValues.get_values()):
                invalid_fields.append(
                    {
                        DbCommonAppKeys.Hidden: self.hidden,
                        CommonKeys.REASON: (
                            '{0} not a valid hidden value'
                            .format(self.hidden)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.uninstallable:
            if self.uninstallable not in UninstallableValues.get_values():
                invalid_fields.append(
                    {
                        DbCommonAppKeys.Uninstallable: self.uninstallable,
                        CommonKeys.REASON: (
                            '{0} not a valid uninstallable value'
                            .format(self.uninstallable)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.release_date:
            if (not isinstance(self.release_date, float) and
                    not isinstance(self.release_date, int)):
                invalid_fields.append(
                    {
                        DbCommonAppKeys.ReleaseDate: self.release_date,
                        CommonKeys.REASON: (
                            '{0} not a valid release date'
                            .format(self.release_date)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )


        if self.vfense_severity:
            if (self.vfense_severity not
                    in CommonSeverityKeys.get_valid_severities()):
                invalid_fields.append(
                    {
                        DbCommonAppKeys.Hidden: self.hidden,
                        CommonKeys.REASON: (
                            '{0} not a valid vfense severity'
                            .format(self.vfense_severity)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.install_date:
            if (not isinstance(self.install_date, float) and
                    not isinstance(self.install_date, int)):
                invalid_fields.append(
                    {
                        DbCommonAppPerAgentKeys.InstallDate: self.install_date,
                        CommonKeys.REASON: (
                            '{0} not a valid install date, float or int only'
                            .format(type(self.install_date))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.last_modified_time:
            if (not isinstance(self.last_modified_time, float) and
                    not isinstance(self.last_modified_time, int)):
                invalid_fields.append(
                    {
                        DbCommonAppPerAgentKeys.LastModifiedTime: (
                            self.last_modified_time
                        ),
                        CommonKeys.REASON: (
                            '{0} not a valid last modified time'
                            .format(self.last_modified_time)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.dependencies:
            if not isinstance(self.dependencies, list):
                invalid_fields.append(
                    {
                        DbCommonAppPerAgentKeys.Dependencies: (
                            self.dependencies
                        ),
                        CommonKeys.REASON: (
                            '{0} not a valid list'.format(self.dependencies)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.views:
            if not isinstance(self.views, list):
                invalid_fields.append(
                    {
                        DbCommonAppPerAgentKeys.Views: (
                            self.views
                        ),
                        CommonKeys.REASON: (
                            '{0} not a valid list'.format(self.views)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        if self.status:
            if self.status not in AppStatuses.get_values():
                invalid_fields.append(
                    {
                        DbCommonAppPerAgentKeys.Status: self.status,
                        CommonKeys.REASON: (
                            '{0} not a valid application status'
                            .format(self.status)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            PackageCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict_apps(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            DbCommonAppKeys.AppId: self.app_id,
            DbCommonAppKeys.Name: self.name,
            DbCommonAppKeys.Hidden: self.hidden,
            DbCommonAppKeys.Description: self.description,
            DbCommonAppKeys.ReleaseDate: self.release_date,
            DbCommonAppKeys.RebootRequired: self.reboot_required,
            DbCommonAppKeys.Kb: self.kb,
            DbCommonAppKeys.SupportUrl: self.support_url,
            DbCommonAppKeys.Version: self.version,
            DbCommonAppKeys.OsCode: self.os_code,
            DbCommonAppKeys.OsString: self.os_string,
            DbCommonAppKeys.vFenseSeverity: self.vfense_severity,
            DbCommonAppKeys.VendorSeverity: self.vendor_severity,
            DbCommonAppKeys.VendorName: self.vendor_name,
            DbCommonAppKeys.FilesDownloadStatus: self.files_download_status,
            DbCommonAppKeys.Uninstallable: self.uninstallable,
            DbCommonAppKeys.Repo: self.repo,
            DbCommonAppKeys.VulnerabilityId: self.vulnerability_id,
            DbCommonAppKeys.VulnerabilityCategories: (
                self.vulnerability_categories
            ),
            DbCommonAppKeys.CveIds: self.cve_ids
        }

    def to_dict_apps_non_null(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """
        data = self.to_dict_apps()

        return {k:data[k] for k in data
                if data[k] != None}

    def to_dict_db_apps(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        data = {
            DbCommonAppKeys.ReleaseDate: (
                DbTime.epoch_time_to_db_time(self.release_date)
            ),
        }

        return dict(self.to_dict_apps().items() + data.items())


    def to_dict_apps_per_agent(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            DbCommonAppPerAgentKeys.Id: self.id,
            DbCommonAppPerAgentKeys.AppId: self.app_id,
            DbCommonAppPerAgentKeys.AgentId: self.agent_id,
            DbCommonAppPerAgentKeys.InstallDate: self.install_date,
            DbCommonAppPerAgentKeys.OsCode: self.os_code,
            DbCommonAppPerAgentKeys.OsString: self.os_string,
            DbCommonAppPerAgentKeys.Update: self.update,
            DbCommonAppPerAgentKeys.Views: self.views,
            DbCommonAppPerAgentKeys.Dependencies: self.dependencies,
            DbCommonAppPerAgentKeys.LastModifiedTime: self.last_modified_time,
            DbCommonAppPerAgentKeys.VulnerabilityCategories: (
                self.vulnerability_categories
            ),
            DbCommonAppPerAgentKeys.VulnerabilityId: self.vulnerability_id,
            DbCommonAppPerAgentKeys.CveIds: self.cve_ids,
            DbCommonAppPerAgentKeys.Status: self.status
        }

    def to_dict_apps_per_agent_non_null(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """
        data = self.to_dict_apps_per_agent()

        return {k:data[k] for k in data
                if data[k] != None}

    def to_dict_db_apps_per_agent(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.
        """
        data = {}
        if (isinstance(self.install_date, int) or
                isinstance(self.install_date, float)):
            data[DbCommonAppPerAgentKeys.InstallDate] = (
                 DbTime.epoch_time_to_db_time(self.install_date)
            )

        if (isinstance(self.last_modified_time, int) or
                isinstance(self.last_modified_time, float)):
            data[DbCommonAppPerAgentKeys.LastModifiedTime] = (
                 DbTime.epoch_time_to_db_time(self.last_modified_time)
            )

        return dict(
            self.to_dict_apps_per_agent_non_null().items() + data.items()
        )


class Files(Base):
    """Used to represent an instance of an app."""

    def __init__(self, file_name=None, file_hash=None, file_size=None,
                 file_uri=None, app_ids=None, agent_ids=None, **kwargs):
        """
        Kwargs:
            file_name (str): Name of the file.
            file_hash (str): The md54 hash of the file.
            file_size (int): Size of the file in kb.
            file_uri (str): The url where this file can be downloaded from.
            app_ids (list): The application ids, this file is associated with.
            agent_ids (list): The agent ids this file is associated with.
        """
        super(Files, self).__init__(**kwargs)
        self.file_name = file_name
        self.file_hash = file_hash
        self.file_size = file_size
        self.download_url = file_uri
        self.app_ids = app_ids
        self.agent_ids = agent_ids

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.agent_ids:
            self.agent_ids = FileDefaults.agent_ids()

        if not self.app_ids:
            self.app_ids= FileDefaults.app_ids()

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

        if self.file_name:
            if len(self.file_name) <= 1:
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
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            FilesKey.FileName: self.file_name,
            FilesKey.AppIds: self.app_ids,
            FilesKey.AgentIds: self.agent_ids,
            FilesKey.FileUri: self.download_url,
            FilesKey.FileHash: self.file_hash,
            FilesKey.FileSize: self.file_size,
        }


class AgentAppData(Base):
    def __init__(self, app_id=None, app_name=None, app_version=None,
                 app_uris=None, cli_options=None, **kwargs
                 ):
        super(AgentAppData, self).__init__(**kwargs)
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = app_version
        self.app_uris = app_uris
        self.cli_options = cli_options


    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            CommonAppKeys.APP_ID: self.app_id,
            CommonAppKeys.APP_NAME: self.app_name,
            CommonAppKeys.APP_VERSION: self.app_version,
            CommonAppKeys.APP_URIS: self.app_uris,
            CommonFileKeys.PKG_CLI_OPTIONS: self.cli_options
        }


class AgentAppFileData(Apps):
    def __init__(self, file_data=None, **kwargs):
        super(AgentAppFileData, self).__init__(**kwargs)
        self.file_data = file_data


    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            DbCommonAppKeys.AppId: self.app_id,
            DbCommonAppKeys.Name: self.app_name,
            DbCommonAppKeys.Version: self.app_version,
            DbCommonAppKeys.FileData: self.file_data,
            DbCommonAppKeys.CliOptions: self.cli_options
        }


class FileUploadData(Base):
    """Used to represent an instance."""

    def __init__(self, file_name=None, file_hash=None, file_size=None,
                 file_path=None, file_uuid=None, **kwargs):
        """
        Kwargs:
            file_name (str): Name of the file.
            file_hash (str): The md5 hash of the file.
            file_size (int): Size of the file in kb.
            file_path (str): The path where this file can be downloaded from.
            file_uuid (str): The primary key of this file.
        """
        super(FileUploadData, self).__init__(**kwargs)
        self.file_name = file_name
        self.file_hash = file_hash
        self.file_size = file_size
        self.file_path = file_path
        self.file_uuid = file_uuid

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            'file_uuid': self.file_uuid,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash
        }
