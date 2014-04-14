from vFense.db.client import r
from time import time

class DbTime():
    time_now = r.epoch_time(int(time()))
    begining_of_time = r.epoch_time(0.0)
