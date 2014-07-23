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
    Arch = 'arch'
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
    AppId = 'app_id'
    Id = 'id'
    InstallDate = 'install_date'
    Status = 'status'
    Hidden = 'hidden'
    AgentId = 'agent_id'
    Dependencies = 'dependencies'
    LastModifiedTime = 'last_modified_time'
    Update = 'update'
    CveIds = 'cve_ids'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    Views = 'views'


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


class CustomAppsKey():
    AppId = 'app_id'
    Views = 'views'
    vFenseAppId = 'vfense_app_id'
    Name = 'name'
    Hidden = 'hidden'
    ViewName = 'view_name'
    Description = 'description'
    ReleaseDate = 'release_date'
    Kb = 'kb'
    FilesDownloadStatus = 'files_download_status'
    RebootRequired = 'reboot_required'
    SupportUrl = 'support_url'
    Version = 'version'
    OsCode = 'os_code'
    vFenseSeverity = 'vfense_severity'
    VendorSeverity = 'vendor_severity'
    VendorName = 'vendor_name'
    CliOptions = 'cli_options'
    Arch = 'arch'
    VulnerabilityId = 'vulnerability_id'
    VulnerabilityCategories = 'vulnerability_categories'
    CveIds = 'cve_ids'


class CustomAppsIndexes():
    AppId = 'app_id'
    Name = 'name'
    vFenseSeverity = 'vfense_severity'
    AppIdAndvFenseSeverity = 'appid_and_vfense_severity'
    NameAndVersion = 'name_and_version'
    Views = 'views'
    ViewAndvFenseSeverity = 'view_and_rvseverity'
    AppIdAndvFenseSeverityAndHidden = 'appid_and_vfense_severity_and_hidden'
    AppIdAndHidden = 'appid_and_hidden'
    ViewAndHidden = 'view_and_hidden'


class CustomAppsPerAgentKey():
    Id = 'id'
    AppId = 'app_id'
    ViewName = 'view_name'
    Name = 'name'
    InstallDate = 'install_date'
    Status = 'status'
    Hidden = 'hidden'
    AgentId = 'agent_id'
    Dependencies = 'dependencies'
    LastModifiedTime = 'last_modified_time'
    Update = 'update'
    CveIds = 'cve_ids'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    Views = 'views'


class CustomAppsPerAgentIndexes():
    AppId = 'app_id'
    AgentId = 'agent_id'
    Status = 'status'
    Views = 'views'
    AppIdAndStatus = 'appid_and_status'
    AgentIdAndAppId = 'agentid_and_appid'
    AppIdAndView = 'appid_and_view'
    StatusAndAgentId = 'status_and_agentid'
    StatusAndView = 'status_and_view'
    StatusAndCveId = 'status_and_cve_id'
    AppIdAndStatusAndView = 'appid_and_status_and_view'


class vFenseAppsKey():
    AppId = 'app_id'
    Views = 'views'
    vFenseAppId = 'vfense_app_id'
    Name = 'name'
    Hidden = 'hidden'
    Description = 'description'
    ReleaseDate = 'release_date'
    Kb = 'kb'
    RebootRequired = 'reboot_required'
    SupportUrl = 'support_url'
    Version = 'version'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    vFenseSeverity = 'vfense_severity'
    VendorSeverity = 'vendor_severity'
    VendorName = 'vendor_name'
    CliOptions = 'cli_options'
    Arch = 'arch'
    VulnerabilityId = 'vulnerability_id'
    VulnerabilityCategories = 'vulnerability_categories'
    CveIds = 'cve_ids'


class vFenseAppsIndexes():
    AppId = 'app_id'
    Name = 'name'
    ViewName = 'view_name'
    vFenseSeverity = 'vfense_severity'
    AppIdAndvFenseSeverity = 'appid_and_vfense_severity'
    NameAndVersion = 'name_and_version'
    Views = 'views'
    ViewAndvFenseSeverity = 'view_and_rvseverity'
    AppIdAndvFenseSeverityAndHidden = 'appid_and_vfense_severity_and_hidden'
    AppIdAndHidden = 'appid_and_hidden'
    ViewAndHidden = 'view_and_hidden'


class vFenseAppsPerAgentKey():
    Id = 'id'
    AppId = 'app_id'
    ViewName = 'view_name'
    Dependencies = 'dependencies'
    Name = 'name'
    InstallDate = 'install_date'
    Status = 'status'
    Hidden = 'hidden'
    AgentId = 'agent_id'
    LastModifiedTime = 'last_modified_time'
    Update = 'update'
    CveIds = 'cve_ids'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    Views = 'views'


class vFenseAppsPerAgentIndexes():
    AppId = 'app_id'
    AgentId = 'agent_id'
    Status = 'status'
    Views = 'views'
    AppIdAndStatus = 'appid_and_status'
    AgentIdAndAppId = 'agentid_and_appid'
    AppIdAndView = 'appid_and_view'
    StatusAndAgentId = 'status_and_agentid'
    StatusAndView = 'status_and_view'
    StatusAndCveId = 'status_and_cve_id'
    AppIdAndStatusAndView = 'appid_and_status_and_view'


####Shared Keys and Indexes###################
class DbCommonAppKeys():
    AppId = 'app_id'
    Name = 'name'
    Hidden = 'hidden'
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
    VulnerabilityId = 'vulnerability_id'
    VulnerabilityCategories = 'vulnerability_categories'
    CveIds = 'cve_ids'
    CliOptions = 'cli_options'


class DbCommonAppPerAgentKeys():
    AppId = 'app_id'
    Id = 'id'
    InstallDate = 'install_date'
    Status = 'status'
    Hidden = 'hidden'
    AgentId = 'agent_id'
    Dependencies = 'dependencies'
    LastModifiedTime = 'last_modified_time'
    Update = 'update'
    CveIds = 'cve_ids'
    OsCode = 'os_code'
    OsStrings = 'os_strings'
    Views = 'views'


class DbCommonAppIndexes():
    AppId = 'app_id'
    Name = 'name'
    vFenseSeverity = 'vfense_severity'
    AppIdAndvFenseSeverity = 'appid_and_vfense_severity'
    NameAndVersion = 'name_and_version'
    AppIdAndvFenseSeverityAndHidden = 'appid_and_vfense_severity_and_hidden'
    AppIdAndHidden = 'appid_and_hidden'


class DbCommonAppPerAgentIndexes():
    AppId = 'app_id'
    AgentId = 'agent_id'
    Status = 'status'
    AppIdAndStatus = 'appid_and_status'
    AgentIdAndAppId = 'agentid_and_appid'
    StatusAndAgentId = 'status_and_agentid'
    AppIdStatusAndAgentId = 'appid_and_status_and_agentid'
    StatusAndCveId = 'status_and_cve_id'
    Views = 'views'
