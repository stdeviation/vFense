from vFense.core.queue.uris import get_result_uris
from json import dumps

print dumps(get_result_uris(version='v2'), indent=4)
