#! /usr/bin/env python
from vFense.db.client import r
from time import time

class DbTime(object):

    @staticmethod
    def time_now():
        return(r.epoch_time(int(time())))

    @staticmethod
    def begining_of_time():
        return(r.epoch_time(0.0))
