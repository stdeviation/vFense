#!/usr/bin/env python

from vFense.db.client import db_connect, r
from vFense.notifications import *
from vFense.plugins.mightymouse import *

Id = 'id'
def initialize_indexes_and_create_tables():
    tables = [
        (FileCollections.FileServers, FileServerKeys.FileServerName),
        (NotificationCollections.NotificationPlugins, Id),
        (NotificationCollections.Notifications, NotificationKeys.NotificationId),
        (NotificationCollections.NotificationsHistory, Id),
    ]
    conn = db_connect()
#################################### If Collections do not exist, create them #########################
    list_of_current_tables = r.table_list().run(conn)
    for table in tables:
        if table[0] not in list_of_current_tables:
            r.table_create(table[0], primary_key=table[1]).run(conn)

#################################### Get All Indexes ###################################################
    file_server_list = r.table(FileCollections.FileServers).index_list().run(conn)
    notif_list = r.table(NotificationCollections.Notifications).index_list().run(conn)
    notif_history_list = r.table(NotificationCollections.NotificationsHistory).index_list().run(conn)
    notif_plugin_list = r.table(NotificationCollections.NotificationPlugins,).index_list().run(conn)

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

#################################### File Server Indexes ###################################################
    if not FileServerIndexes.ViewName in file_server_list:
        r.table(FileCollections.FileServers).index_create(FileServerIndexes.ViewName).run(conn)

#################################### Close Database Connection ###################################################
    conn.close()
