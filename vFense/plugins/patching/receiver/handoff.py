from vFense.core.receiver.handoff import HandOff
from vFense.plugins.patching.apps.manager import (
   incoming_applications_from_agent
)
from vFense.plugins.patching.apps.custom.manager import CustomAppsManager
from vFense.plugins.patching.apps.supported_apps.syncer import (
    get_all_supported_apps_for_agent
)

class PatcherHandOff(HandOff):
    def __init__(self, apps_data=None, **kwargs):
        super(PatcherHandOff, self).__init__(**kwargs)
        self.apps_data = apps_data

    def new_agent_operation(self):
        self.add_applications_from_agent()
        self.add_custom_apps()
        #self.add_supported_apps()

    def startup_operation(self, apps_data):
        self.refresh_apps_operation()

    def refresh_apps_operation(self):
        self.add_applications_from_agent()
        #self.add_supported_apps()

    def available_agent_update_operation(self):
        self.add_applications_from_agent()

    def add_custom_apps(self):
        manager = CustomAppsManager()
        manager.add_apps_to_agents.delay(None, self.agent_id)

    def add_supported_apps(self):
        get_all_supported_apps_for_agent.delay(self.agent_id)

    def add_applications_from_agent(self):
        incoming_applications_from_agent.delay(
            self.agent_id, self.apps_data, self.delete_afterwards
        )
