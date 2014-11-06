import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections,
    HardwarePerAgentIndexes, HardwarePerAgentKeys
)
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsPerAgentKeys, TagsPerAgentIndexes
)
from vFense.core.agent.search._db import FetchAgents
from vFense.plugins.patching._db_model import (
    AppCollections, AppsKey, AppsPerAgentIndexes
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.decorators import time_it, catch_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class FetchHardware(FetchAgents):
    """Agent database queries"""
    def __init__(self, **kwargs):
        """
        Kwargs:
            view_name (str): Fetch all agents in this view.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """
        super(FetchHardware, self).__init__(**kwargs)
        self.keys_to_pluck = [
            AgentKeys.ComputerName, AgentKeys.HostName, AgentKeys.DisplayName,
            AgentKeys.OsCode, AgentKeys.OsString, AgentKeys.AgentId,
            AgentKeys.AgentStatus, AgentKeys.MachineType, AgentKeys.SysArch
        ]

        return(count, data)

    def _set_merge_query(self):
        merge_query = (
            lambda x:
            {
                TagCollections.Tags: (
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        x[TagsPerAgentKeys.AgentId],
                        index=TagsPerAgentIndexes.AgentId
                    )
                    .eq_join(
                        TagKeys.TagId,
                        r.table(TagCollections.Tags)
                    )
                    .zip()
                    .pluck(
                        TagsPerAgentKeys.TagId,
                        TagsPerAgentKeys.TagName
                    )
                    .coerce_to('array')
                ),
                AgentCommonKeys.AVAIL_UPDATES: (
                    r
                    .table(AppCollections.AppsPerAgent)
                    .get_all(
                        [
                            CommonAppKeys.AVAILABLE,
                            x[AgentKeys.AgentId]
                        ],
                        index=AppsPerAgentIndexes.StatusAndAgentId
                    )
                    .count()
                ),
                AgentCommonKeys.AVAIL_VULN: (
                    r
                    .table(AppCollections.AppsPerAgent)
                    .get_all(
                        [
                            CommonAppKeys.AVAILABLE,
                            x[AgentKeys.AgentId]
                        ],
                        index=AppsPerAgentIndexes.StatusAndAgentId
                    )
                    .eq_join(
                        lambda y:
                        y[AppsKey.AppId],
                        r.table(AppCollections.UniqueApplications)
                    )
                    .zip()
                    .filter(
                        lambda z:
                        z[AppsKey.VulnerabilityId] != ''
                    )
                    .count()
                ),
                AgentKeys.LastAgentUpdate: (
                    x[AgentKeys.LastAgentUpdate].to_epoch_time()
                ),
                AgentKeys.DateAdded: (
                    x[AgentKeys.DateAdded].to_epoch_time()
                )
            }
        )

        return(merge_query)

    def _set_agent_base_query(self):
        base_filter = (
            r
            .table(AgentCollections.Agents)
        )
        if self.view_name:
            base_filter = (
                r
                .table(AgentCollections.Agents)
                .get_all(
                    self.view_name,
                    index=AgentKeys.Views
                )
            )

        return(base_filter)

    def _set_hw_base_query_by_nic(self):
        base_filter = (
            r
            .table(AgentCollections.Agents)
            .eq_join(
                lambda x: [
                    x[AgentKeys.AgentId],
                    HardwarePerAgentKeys.Nic
                ],
                r.table(AgentCollections.Hardware),
                index=HardwarePerAgentIndexes.AgentIdAndType
            )
            .zip()
        )
        base_count = (
            r
            .table(AgentCollections.Agents)
            .eq_join(
                lambda x: [
                    x[AgentKeys.AgentId],
                    HardwarePerAgentKeys.Nic
                ],
                r.table(AgentCollections.Hardware),
                index=HardwarePerAgentIndexes.AgentIdAndType
            )
            .zip()
        )
        if self.view_name:
            base_count = (
                r
                .table(AgentCollections.Agents)
                .get_all(self.view_name, index=AgentIndexes.Views)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        HardwarePerAgentKeys.Nic
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )

            base_filter = (
                r
                .table(AgentCollections.Agents)
                .get_all(self.view_name, index=AgentIndexes.Views)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        HardwarePerAgentKeys.Nic
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )

        return(base_count, base_filter)
