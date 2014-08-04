class AppCollections():
    UniqueApplications = 'unique_applications'
    OsApps = 'os_apps'
    AppsPerAgent = 'apps_per_agent'
    CustomApps = 'custom_apps'
    CustomAppsPerAgent = 'custom_apps_per_agent'
    SupportedApps = 'supported_apps'
    SupportedAppsPerAgent = 'supported_apps_per_agent'
    vFenseApps = 'vfense_apps'
    vFenseAppsPerAgent = 'vfense_apps_per_agent'


class DownloadCollections():
    LatestDownloadedSupported = 'latest_downloaded_supported'
    LatestDownloadedAgent = 'latest_downloaded_agent'


class FileCollections():
    Files = 'files'
    FileServers = 'file_servers'


class FilesKey():
    AppIds = 'app_ids'
    AgentIds = 'agent_ids'
    FileName = 'file_name'
    FileSize = 'file_size'
    FileUri = 'file_uri'
    FileHash = 'file_hash'


class FilesIndexes():
    AppId = 'app_id'
    FilesDownloadStatus = 'files_download_status'


class FileServerKeys():
    FileServerName = 'file_server_name'
    Views = 'views'
    Address = 'address'


class FileServerIndexes():
    ViewName = 'view_name'


class AppsKey():
    AppId = 'app_id'
    Name = 'name'
    Hidden = 'hidden'
    Views = 'views'
    Description = 'description'
    ReleaseDate = 'release_date'
    RebootRequired = 'reboot_required'
    Kb = 'kb'
    SupportUrl = 'support_url'
    Version = 'version'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    vFenseSeverity = 'vfense_severity'
    VendorSeverity = 'vendor_severity'
    VendorName = 'vendor_name'
    FilesDownloadStatus = 'files_download_status'
    FileData = 'file_data'
    Arch = 'arch'
    Uninstallable = 'uninstallable'
    Repo = 'repo'
    VulnerabilityId = 'vulnerability_id'
    VulnerabilityCategories = 'vulnerability_categories'
    CveIds = 'cve_ids'


class AppsIndexes():
    AppId = 'app_id'
    Name = 'name'
    Views = 'views'
    vFenseSeverity = 'vfense_severity'
    AppIdAndvFenseSeverity = 'appid_and_vfense_severity'
    NameAndVersion = 'name_and_version'
    AppIdAndvFenseSeverityAndHidden = 'appid_and_vfense_severity_and_hidden'
    AppIdAndHidden = 'appid_and_hidden'


class AppsPerAgentKey():
    Id = 'id'
    AppId = 'app_id'
    InstallDate = 'install_date'
    Status = 'status'
    AgentId = 'agent_id'
    Dependencies = 'dependencies'
    LastModifiedTime = 'last_modified_time'
    Update = 'update'
    OsCode = 'os_code'
    OsString = 'os_string'
    Views = 'views'
    VulnerabilityId = 'vulnerability_id'
    VulnerabilityCategories = 'vulnerability_categories'
    CveIds = 'cve_ids'


class AppsPerAgentIndexes():
    AppId = 'app_id'
    AgentId = 'agent_id'
    Status = 'status'
    Views = 'views'
    AppIdAndStatus = 'appid_and_status'
    AgentIdAndAppId = 'agentid_and_appid'
    StatusAndAgentId = 'status_and_agentid'
    AppIdStatusAndAgentId = 'appid_and_status_and_agentid'
    StatusAndCveId = 'status_and_cve_id'


class CustomAppsKey(AppsKey):
    vFenseAppId = 'vfense_app_id'
    CliOptions = 'cli_options'


class CustomAppsIndexes(AppsIndexes):
    pass


class CustomAppsPerAgentKey(AppsPerAgentKey):
    pass


class CustomAppsPerAgentIndexes(AppsPerAgentIndexes):
    pass

class vFenseAppsKey(AppsKey):
    vFenseAppId = 'vfense_app_id'
    CliOptions = 'cli_options'


class vFenseAppsIndexes(AppsIndexes):
    pass

class vFenseAppsPerAgentKey(AppsPerAgentKey):
    pass


class vFenseAppsPerAgentIndexes(AppsPerAgentIndexes):
    pass


####Shared Keys and Indexes###################
class DbCommonAppKeys(AppsKey):
    CliOptions = 'cli_options'
    vFenseAppId = 'vfense_app_id'


class DbCommonAppPerAgentKeys(AppsPerAgentKey):
    pass


class DbCommonAppIndexes(AppsIndexes):
    pass


class DbCommonAppPerAgentIndexes(AppsPerAgentIndexes):
    pass
