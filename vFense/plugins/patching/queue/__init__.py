from vFense.core.queue import AgentQueueOperation
from vFense.plugins.patching.operations._constants import InstallKeys


class InstallQueueOperation(AgentQueueOperation):
    def __init__(self, restart=None, file_data=None, cpu_throttle=None,
                 net_throttle=None, **kwargs
                 ):
        super(InstallQueueOperation, self).__init__(**kwargs)
        self.restart = restart
        self.file_data = file_data
        self.cpu_throttle = cpu_throttle
        self.net_throttle = net_throttle

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """
        data = super(InstallQueueOperation, self).to_dict()
        data[InstallKeys.RESTART] = self.restart
        data[InstallKeys.CPU_THROTTLE] = self.cpu_throttle
        data[InstallKeys.NET_THROTTLE] = self.net_throttle
        data[InstallKeys.FILE_DATA] = self.file_data

        return data


