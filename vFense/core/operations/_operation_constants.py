from vFense.core._constants import Time
class OperationDefaults():
    @staticmethod
    def updated_time():
        return 0

    @staticmethod
    def completed_time():
        return 0

    @staticmethod
    def created_time():
        return Time.now()

    @staticmethod
    def agents():
        return list()

    @staticmethod
    def agent_ids():
        return list()

    @staticmethod
    def cpu_throttle():
        return 'normal'

    @staticmethod
    def net_throttle():
        return 0

    @staticmethod
    def agents_total_count():
        return 0

    @staticmethod
    def agents_failed_count():
        return 0

    @staticmethod
    def agents_completed_count():
        return 0

    @staticmethod
    def agents_expired_count():
        return 0

    @staticmethod
    def agents_pending_results_count():
        return 0

    @staticmethod
    def agents_pending_pickup_count():
        return 0

    @staticmethod
    def agents_completed_with_errors_count():
        return 0

    @staticmethod
    def applications():
        return list()
