import threading
from datetime import datetime
import os
from pathlib import Path

from cmnUtils import safeOpen


class Schedule:

    def __init__(self, directory):
        self.lock = threading.Lock()
        self.directory = directory
        safeOpen.mkdir_p(str(directory))
        self.mem_sched = {}

    def add(self, uid, date):
        timestamp_obj = datetime.timestamp(date)
        self.lock.acquire()
        ids = self._get_ids(timestamp_obj)

        if uid not in ids:
            self.mem_sched[timestamp_obj].append(uid)
            self._append_to_date(uid, timestamp_obj)
        self.lock.release()

    def remove(self, uid, date):
        timestamp_obj = datetime.timestamp(date)
        self.lock.acquire()
        ids = self._get_ids(timestamp_obj)

        if uid in ids:
            self.mem_sched[timestamp_obj].remove(uid)
            self._update_date(timestamp_obj)
        self.lock.release()

    def get(self, date) -> list:
        self.lock.acquire()
        timestamp_obj = datetime.timestamp(date)
        ids = self._get_ids(timestamp_obj)
        self.lock.release()
        return ids

    def get_week(self, date) -> list:
        dt_object = datetime.fromtimestamp(date)
        week_num = dt_object.strftime("%V")
        # TODO: this function doesn't work yet
        return []

    # stores everything on given date
    def _update_date(self, timestamp_obj):
        f = open(str(self._get_file(timestamp_obj)), "w+")
        f.writelines(self.mem_sched[timestamp_obj])
        f.close()

    # appends just 1 item
    def _append_to_date(self, uid, timestamp_obj):
        f = open(str(self._get_file(timestamp_obj)), "a+")
        f.write(uid + '\n')
        f.close()

    # read from file, return empty list if file doesn't exist
    def _read_file(self, timestamp_obj) -> list:
        # load in from disc
        filename = self._get_file(timestamp_obj)
        # create file if doesn't exist (a+)
        try:
            with open(str(filename), "r+") as f:
                print(filename)
                ids = f.readlines()
            return ids
        except FileNotFoundError:
            return []

    def _get_ids(self, timestamp_obj) -> list:
        try:
            ids = self.mem_sched[timestamp_obj]
        except KeyError:
            ids = self.mem_sched[timestamp_obj] = self._read_file(timestamp_obj)
        return ids

    def _get_file(self, timestamp_obj) -> Path:
        return self.directory / Path(str(timestamp_obj) + ".txt")

