#!/usr/bin/env python

from vFense.db.client import db_connect, r

from vFense.core.agent._db_model import *
from vFense.core.tag._db_model import *
from vFense.core.user._db_model import *
from vFense.core.group._db_model import *
from vFense.core.view._db_model import *
from vFense.core.queue._db_model import *

from vFense.notifications import *
from vFense.core.operations._db_model import *
from vFense.plugins.patching._db_model import *
from vFense.plugins.mightymouse import *
from vFense.plugins.vuln.cve._db_model import *
from vFense.plugins.vuln.ubuntu._db_model import *
from vFense.plugins.vuln.ubuntu._constants import UbuntuVulnSubKeys
from vFense.plugins.vuln.redhat._db_model import *
from vFense.plugins.vuln.windows._db_model import *
from vFense.plugins.vuln.windows._constants import WindowsVulnSubKeys
from vFense.core.queue import *

Id = 'id'
def initialize_indexes_and_create_tables():
    tables = [
        (AgentCollections.Agents, AgentKeys.AgentId),
        (QueueCollections.Agent, AgentQueueKey.Id),
        (AppCollections.UniqueApplications, AppsKey.AppId),
        (AppCollections.AppsPerAgent, Id),
        (AppCollections.CustomApps, CustomAppsKey.AppId),
        (AppCollections.CustomAppsPerAgent, Id),
        (AppCollections.vFenseApps, vFenseAppsKey.AppId),
        (AppCollections.vFenseAppsPerAgent, Id),
        (FileCollections.Files, FilesKey.FileName),
        (FileCollections.FileServers, FileServerKeys.FileServerName),
        (CVECollections.CVE, CveKeys.CveId),
        (WindowsVulnerabilityCollections.Vulnerabilities, WindowsVulnerabilityKeys.VulnerabilityId),
        (UbuntuVulnerabilityCollections.Vulnerabilities, UbuntuVulnerabilityKeys.VulnerabilityId),
        (RedHatVulnerabilityCollections.Vulnerabilities, RedhatVulnerabilityKeys.VulnerabilityId),
        ('downloaded_status', Id),
        (AgentCollections.Hardware, Id),
        (NotificationCollections.NotificationPlugins, Id),
        (NotificationCollections.Notifications, NotificationKeys.NotificationId),
        (NotificationCollections.NotificationsHistory, Id),
        ('notification_queue', Id),
        (OperationCollections.Agent, AgentOperationKey.OperationId),
        (OperationCollections.Admin, AgentOperationKey.OperationId),
        (OperationCollections.OperationPerAgent, Id),
        (OperationCollections.OperationPerApp, Id),
        ('plugin_configurations', 'name'),
        (TagCollections.Tags, TagKeys.TagId),
        (TagCollections.TagsPerAgent, Id),
        (UserCollections.Users, UserKeys.UserName),
        (GroupCollections.Groups, GroupKeys.GroupId),
        (ViewCollections.Views, ViewKeys.ViewName),
    ]
    conn = db_connect()
#################################### If Collections do not exist, create them #########################
    list_of_current_tables = r.table_list().run(conn)
    for table in tables:
        if table[0] not in list_of_current_tables:
            r.table_create(table[0], primary_key=table[1]).run(conn)

#################################### Get All Indexes ###################################################
    app_list = r.table(AppCollections.AppsPerAgent).index_list().run(conn)
    unique_app_list = r.table(AppCollections.UniqueApplications).index_list().run(conn)
    downloaded_list = r.table('downloaded_status').index_list().run(conn)
    custom_app_list = r.table(AppCollections.CustomApps).index_list().run(conn)
    custom_app_per_agent_list = r.table(AppCollections.CustomAppsPerAgent).index_list().run(conn)
    vfense_app_list = r.table(AppCollections.vFenseApps).index_list().run(conn)
    vfense_app_per_agent_list = r.table(AppCollections.vFenseAppsPerAgent).index_list().run(conn)
    cve_list = r.table(CVECollections.CVE).index_list().run(conn)
    windows_bulletin_list = r.table(WindowsVulnerabilityCollections.Vulnerabilities).index_list().run(conn)
    ubuntu_bulletin_list = r.table(UbuntuVulnerabilityCollections.Vulnerabilities).index_list().run(conn)
    files_list = r.table(FileCollections.Files).index_list().run(conn)
    file_server_list = r.table(FileCollections.FileServers).index_list().run(conn)
    tags_list = r.table(TagCollections.Tags).index_list().run(conn)
    agents_list = r.table(AgentCollections.Agents).index_list().run(conn)
    agent_operations_list = r.table(OperationCollections.Agent).index_list().run(conn)
    admin_operations_list = r.table(OperationCollections.Admin).index_list().run(conn)
    operations_per_agent_list = r.table(OperationCollections.OperationPerAgent).index_list().run(conn)
    operations_per_app_list = r.table(OperationCollections.OperationPerApp).index_list().run(conn)
    notif_list = r.table(NotificationCollections.Notifications).index_list().run(conn)
    notif_history_list = r.table(NotificationCollections.NotificationsHistory).index_list().run(conn)
    hw_per_agent_list = r.table(AgentCollections.Hardware).index_list().run(conn)
    tag_per_agent_list = r.table(TagCollections.TagsPerAgent).index_list().run(conn)
    notif_plugin_list = r.table(NotificationCollections.NotificationPlugins,).index_list().run(conn)
    agent_queue_list = r.table(QueueCollections.Agent).index_list().run(conn)
    user_list = r.table(UserCollections.Users).index_list().run(conn)
    groups_list = r.table(GroupCollections.Groups).index_list().run(conn)
    view_list = r.table(ViewCollections.Views).index_list().run(conn)

#################################### AgentsColleciton Indexes ###################################################
    if not AgentIndexes.Views in agents_list:
        r.table(AgentCollections.Agents).index_create(AgentIndexes.Views, multi=True).run(conn)

    if not AgentIndexes.OsCode in agents_list:
        r.table(AgentCollections.Agents).index_create(AgentIndexes.OsCode).run(conn)

#################################### AppsCollection Indexes ###################################################
    if not AppsIndexes.vFenseSeverity in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(AppsIndexes.vFenseSeverity).run(conn)

    if not AppsIndexes.Name in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(AppsIndexes.Name).run(conn)

    if not AppsIndexes.NameAndVersion in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(
            AppsIndexes.NameAndVersion, lambda x: [
                x[AppsKey.Name], x[AppsKey.Version]]).run(conn)

    if not AppsIndexes.AppIdAndvFenseSeverity in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(
            AppsIndexes.AppIdAndvFenseSeverity, lambda x: [
                x[AppsKey.AppId],
                x[AppsKey.vFenseSeverity]]).run(conn)


#################################### FilesColleciton Indexes ###################################################
    if not FilesIndexes.FilesDownloadStatus in files_list:
        r.table(FileCollections.Files).index_create(FilesIndexes.FilesDownloadStatus).run(conn)

#################################### AppsPerAgentCollection Indexes ###################################################
    if not AppsPerAgentIndexes.Status in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.Status).run(conn)

    if not AppsPerAgentIndexes.AgentId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.AgentId).run(conn)

    if not AppsPerAgentIndexes.AppId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.AppId).run(conn)

    if not AppsPerAgentIndexes.AgentIdAndAppId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[AppsPerAgentKey.AgentId], x[AppsPerAgentKey.AppId]]).run(conn)

    if not AppsPerAgentIndexes.AppIdAndStatus in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[AppsPerAgentKey.AppId], x[AppsPerAgentKey.Status]]).run(conn)

    if not AppsPerAgentIndexes.StatusAndAgentId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[AppsPerAgentKey.Status], x[AppsPerAgentKey.AgentId]]).run(conn)


#################################### TagsCollection Indexes ###################################################
    if not TagsIndexes.ViewName in tags_list:
        r.table(TagCollections.Tags).index_create(TagsIndexes.ViewName).run(conn)

    if not TagsIndexes.TagNameAndView in tags_list:
        r.table(TagCollections.Tags).index_create(
            TagsIndexes.TagNameAndView, lambda x: [
                x[TagKeys.ViewName], x[TagKeys.TagName]]).run(conn)

#################################### TagsPerAgentCollection Indexes ###################################################
    if not TagsPerAgentIndexes.TagId in tag_per_agent_list:
        r.table(TagCollections.TagsPerAgent).index_create(TagsPerAgentIndexes.TagId).run(conn)

    if not TagsPerAgentIndexes.AgentId in tag_per_agent_list:
        r.table(TagCollections.TagsPerAgent).index_create(TagsPerAgentIndexes.AgentId).run(conn)

    if not TagsPerAgentIndexes.AgentIdAndTagId in tag_per_agent_list:
        r.table(TagCollections.TagsPerAgent).index_create(
            TagsPerAgentIndexes.AgentIdAndTagId, lambda x: [
                x[TagsPerAgentKeys.AgentId],
                x[TagsPerAgentKeys.TagId]]).run(conn)


#################################### CustomAppsCollection Indexes ###################################################
    if not CustomAppsIndexes.vFenseSeverity in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(CustomAppsIndexes.vFenseSeverity).run(conn)

    if not CustomAppsIndexes.Name in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(CustomAppsIndexes.Name).run(conn)

    if not CustomAppsIndexes.NameAndVersion in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(
            CustomAppsIndexes.NameAndVersion, lambda x: [
                x[CustomAppsKey.Name], x[CustomAppsKey.Version]]).run(conn)


    if not CustomAppsIndexes.AppIdAndvFenseSeverity in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(
            CustomAppsIndexes.AppIdAndvFenseSeverity, lambda x: [
                x[CustomAppsKey.AppId],
                x[CustomAppsKey.vFenseSeverity]]).run(conn)

#################################### CustomAppsPerAgentCollection Indexes ###################################################
    if not CustomAppsPerAgentIndexes.Status in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.Status).run(conn)

    if not CustomAppsPerAgentIndexes.AgentId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.AgentId).run(conn)

    if not CustomAppsPerAgentIndexes.AppId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.AppId).run(conn)

    if not CustomAppsPerAgentIndexes.AgentIdAndAppId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[CustomAppsPerAgentKey.AgentId], x[CustomAppsPerAgentKey.AppId]]).run(conn)


    if not CustomAppsPerAgentIndexes.AppIdAndStatus in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[CustomAppsPerAgentKey.AppId], x[CustomAppsPerAgentKey.Status]]).run(conn)

    if not CustomAppsPerAgentIndexes.StatusAndAgentId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[CustomAppsPerAgentKey.Status], x[CustomAppsPerAgentKey.AgentId]]).run(conn)

#################################### vFenseAppsCollection Indexes ###################################################
    if not vFenseAppsIndexes.vFenseSeverity in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(vFenseAppsIndexes.vFenseSeverity).run(conn)

    if not vFenseAppsIndexes.Name in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(vFenseAppsIndexes.Name).run(conn)

    if not vFenseAppsIndexes.NameAndVersion in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(
            vFenseAppsIndexes.NameAndVersion, lambda x: [
                x[vFenseAppsKey.Name], x[vFenseAppsKey.Version]]).run(conn)


    if not vFenseAppsIndexes.AppIdAndvFenseSeverity in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(
            vFenseAppsIndexes.AppIdAndvFenseSeverity, lambda x: [
                x[vFenseAppsKey.AppId],
                x[vFenseAppsKey.vFenseSeverity]]).run(conn)

#################################### vFenseAppsPerAgentCollection Indexes ###################################################
    if not vFenseAppsPerAgentIndexes.Status in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(vFenseAppsPerAgentIndexes.Status).run(conn)

    if not vFenseAppsPerAgentIndexes.AgentId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(vFenseAppsPerAgentIndexes.AgentId).run(conn)

    if not vFenseAppsPerAgentIndexes.AppId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(vFenseAppsPerAgentIndexes.AppId).run(conn)

    if not vFenseAppsPerAgentIndexes.AgentIdAndAppId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[vFenseAppsPerAgentKey.AgentId], x[vFenseAppsPerAgentKey.AppId]]).run(conn)

    if not vFenseAppsPerAgentIndexes.AppIdAndStatus in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[vFenseAppsPerAgentKey.AppId], x[vFenseAppsPerAgentKey.Status]]).run(conn)

    if not vFenseAppsPerAgentIndexes.StatusAndAgentId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[vFenseAppsPerAgentKey.Status], x[vFenseAppsPerAgentKey.AgentId]]).run(conn)


#################################### AgentOperationsCollection Indexes ###################################################
    if not AgentOperationIndexes.ViewName in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.ViewName).run(conn)

    if not AgentOperationIndexes.TagId in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.TagId).run(conn)

    if not AgentOperationIndexes.Operation in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.Operation).run(conn)

    if not AgentOperationIndexes.AgentIds in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationIndexes.AgentIds, multi=True).run(conn)

    if not AgentOperationIndexes.OperationAndView in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.OperationAndView, lambda x: [
                x[AgentOperationKey.Operation],
                x[AgentOperationKey.ViewName]]).run(conn)

    if not AgentOperationIndexes.PluginAndView in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.PluginAndView, lambda x: [
                x[AgentOperationKey.Plugin],
                x[AgentOperationKey.ViewName]]).run(conn)

    if not AgentOperationIndexes.CreatedByAndView in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.CreatedByAndView, lambda x: [
                x[AgentOperationKey.CreatedBy],
                x[AgentOperationKey.ViewName]]).run(conn)

#################################### OperationsPerAgentCollection Indexes ###################################################
    if not OperationPerAgentIndexes.OperationId in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(OperationPerAgentKey.OperationId).run(conn)

    if not OperationPerAgentIndexes.AgentIdAndView in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.AgentIdAndView, lambda x: [
                x[OperationPerAgentKey.AgentId],
                x[OperationPerAgentKey.ViewName]]).run(conn)

    if not OperationPerAgentIndexes.TagIdAndView in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.TagIdAndView, lambda x: [
                x[OperationPerAgentKey.TagId],
                x[OperationPerAgentKey.ViewName]]).run(conn)

    if not OperationPerAgentIndexes.StatusAndView in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.StatusAndView, lambda x: [
                x[OperationPerAgentKey.Status],
                x[OperationPerAgentKey.ViewName]]).run(conn)

    if not OperationPerAgentIndexes.OperationIdAndAgentId in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.OperationIdAndAgentId, lambda x: [
                x[OperationPerAgentKey.OperationId],
                x[OperationPerAgentKey.AgentId]]).run(conn)

#################################### OperationsPerAppCollection Indexes ###################################################
    if not OperationPerAppIndexes.OperationId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(OperationPerAppKey.OperationId).run(conn)

    if not OperationPerAppIndexes.OperationIdAndAgentId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(
            OperationPerAppIndexes.OperationIdAndAgentId, lambda x: [
                x[OperationPerAppKey.OperationId],
                x[OperationPerAppKey.AgentId]]).run(conn)

    if not OperationPerAppIndexes.OperationIdAndAgentIdAndAppId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(
            OperationPerAppIndexes.OperationIdAndAgentIdAndAppId, lambda x: [
                x[OperationPerAppKey.OperationId],
                x[OperationPerAppKey.AgentId],
                x[OperationPerAppKey.AppId]]).run(conn)

#################################### HardwarePerAgentCollection Indexes ###################################################
    if not HardwarePerAgentIndexes.Type in hw_per_agent_list:
        r.table(AgentCollections.Hardware).index_create(HardwarePerAgentIndexes.Type).run(conn)

    if not HardwarePerAgentIndexes.AgentId in hw_per_agent_list:
        r.table(AgentCollections.Hardware).index_create(HardwarePerAgentIndexes.AgentId).run(conn)

    if not HardwarePerAgentIndexes.AgentIdAndType in hw_per_agent_list:
        r.table(AgentCollections.Hardware).index_create(
            HardwarePerAgentIndexes.AgentIdAndType,
            lambda x: [
                x[HardwarePerAgentKeys.AgentId],
                x[HardwarePerAgentKeys.Type],
            ]
        ).run(conn)

#################################### DownloadStatusCollection Indexes ###################################################
    if not 'app_id' in downloaded_list:
        r.table('downloaded_status').index_create('app_id').run(conn)

    if not 'by_filename_and_rvid' in downloaded_list:
        r.table('downloaded_status').index_create(
            'by_filename_and_rvid', lambda x: [
                x['file_name'], x['app_id']]).run(conn)

#################################### NotificationsCollection Indexes ###################################################
    if not NotificationIndexes.ViewName in notif_list:
        r.table(NotificationCollections.Notifications).index_create(NotificationKeys.ViewName).run(conn)

    if not NotificationIndexes.RuleNameAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.RuleNameAndView, lambda x: [
                x[NotificationKeys.RuleName],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.NotificationTypeAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.NotificationTypeAndView, lambda x: [
                x[NotificationKeys.NotificationType],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.AppThresholdAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.AppThresholdAndView, lambda x: [
                x[NotificationKeys.AppThreshold],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.RebootThresholdAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.RebootThresholdAndView, lambda x: [
                x[NotificationKeys.RebootThreshold],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.ShutdownThresholdAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.ShutdownThresholdAndView, lambda x: [
                x[NotificationKeys.ShutdownThreshold],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.CpuThresholdAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.CpuThresholdAndView, lambda x: [
                x[NotificationKeys.CpuThreshold],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.MemThresholdAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.MemThresholdAndView, lambda x: [
                x[NotificationKeys.MemThreshold],
                x[NotificationKeys.ViewName]]).run(conn)

    if not NotificationIndexes.FileSystemThresholdAndFileSystemAndView in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.FileSystemThresholdAndFileSystemAndView, lambda x: [
                x[NotificationKeys.FileSystemThreshold],
                x[NotificationKeys.FileSystem],
                x[NotificationKeys.ViewName]]).run(conn)

#################################### NotificationsHistory Indexes ###################################################
    if not NotificationHistoryIndexes.NotificationId in notif_history_list:
        r.table(NotificationCollections.NotificationsHistory).index_create(NotificationHistoryKeys.NotificationId).run(conn)

#################################### NotificationsPlugin Indexes ###################################################
    if not NotificationPluginIndexes.ViewName in notif_plugin_list:
        r.table(NotificationCollections.NotificationPlugins).index_create(NotificationPluginKeys.ViewName).run(conn)

#################################### Cve Indexes ###################################################
    if not CveIndexes.Categories in cve_list:
        r.table(CVECollections.CVE).index_create(CveIndexes.Categories, multi=True).run(conn)

#################################### Windows Bulletin Indexes ###################################################
    if not WindowsVulnerabilityIndexes.ComponentKb in windows_bulletin_list:
        (
            r
            .table(WindowsVulnerabilityCollections.Vulnerabilities)
            .index_create(
                WindowsVulnerabilityIndexes.ComponentKb,
                lambda x:
                    x[WindowsVulnerabilityKeys.Apps].map(
                        lambda y: y[WindowsVulnSubKeys.KB]
                    ),
                multi=True
            )
            .run(conn)
        )

    if not WindowsVulnerabilityIndexes.CveIds in windows_bulletin_list:
        r.table(WindowsVulnerabilityCollections.Vulnerabilities).index_create(WindowsVulnerabilityIndexes.CveIds, multi=True).run(conn)

#################################### Ubuntu Bulletin Indexes ###################################################
    if not UbuntuVulnerabilityIndexes.NameAndVersion in ubuntu_bulletin_list:
        r.table(UbuntuVulnerabilityCollections.Vulnerabilities).index_create(
            UbuntuVulnerabilityIndexes.NameAndVersion, lambda x:
                x[UbuntuVulnerabilityKeys.Apps].map(lambda y:
                    [y[UbuntuVulnSubKeys.NAME], y[UbuntuVulnSubKeys.VERSION]]), multi=True).run(conn)

#################################### Agent Queue Indexes ###################################################
    if not AgentQueueIndexes.AgentId in agent_queue_list:
        r.table(QueueCollections.Agent).index_create(AgentQueueIndexes.AgentId).run(conn)

#################################### User Indexes ###################################################
    if not UserIndexes.Views in user_list:
        r.table(UserCollections.Users).index_create(UserIndexes.Views, multi=True).run(conn)

#################################### View Indexes ###################################################
    if not ViewIndexes.Users in view_list:
        r.table(ViewCollections.Views).index_create(ViewIndexes.Users, multi=True).run(conn)

    if not ViewIndexes.Token in view_list:
        r.table(ViewCollections.Views).index_create(ViewIndexes.Token).run(conn)

    if not ViewIndexes.PreviousTokens in view_list:
        r.table(ViewCollections.Views).index_create(ViewIndexes.PreviousTokens, multi=True).run(conn)

#################################### Group Indexes ###################################################
    if not GroupIndexes.Views in groups_list:
        r.table(GroupCollections.Groups).index_create(GroupIndexes.Views, multi=True).run(conn)

    if not GroupIndexes.Users in groups_list:
        r.table(GroupCollections.Groups).index_create(GroupIndexes.Users, multi=True).run(conn)

    if not GroupIndexes.GroupName in groups_list:
        r.table(GroupCollections.Groups).index_create(GroupIndexes.GroupName).run(conn)

#################################### File Server Indexes ###################################################
    if not FileServerIndexes.ViewName in file_server_list:
        r.table(FileCollections.FileServers).index_create(FileServerIndexes.ViewName).run(conn)

#################################### Close Database Connection ###################################################
    conn.close()
