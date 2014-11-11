from vFense.db.client import rq_settings

REDIS_HOST, REDIS_PORT , REDIS_DB = rq_settings()

# You can also specify the Redis DB to use
# REDIS_DB = 3
# REDIS_PASSWORD = 'very secret'

# Queues to listen on
QUEUES = ['downloader']
