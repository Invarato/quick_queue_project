# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import gc
import itertools
import logging
import multiprocessing
import os
import sys
import time
from datetime import datetime

try:
    import queue
except ImportError:
    # python 3.x
    import Queue as queue

from quick_queue.quick_queue import QQueue

"""
Execute this script to see sorted result in console

iterable_with_data_to_sort: any iterable with data to sort
tmp_dir: temporal folder to sort in disk
"""
iterable_with_data = [
    "key3|value3",
    "key1|value1",
    "key2|value2"
]
times_repeat = 100000
logging_level = logging.DEBUG
queue_max_size = 1000

def _is_parent_process_killed():
    """
    Return if parent process was killed
    :return: True if parent process was killed
    """
    return os.getppid() == 1


def _mprocess(qq,
              init_args,
              proxy_start_event,
              proxy_end_event,
              logging_level):
    logging.basicConfig(stream=sys.stderr, level=logging_level)

    logging.debug("[START GETTER -> ppid:{} | pid:{}]".format(os.getppid(), os.getpid()))
    proxy_start_event.set()
    gc.collect()

    qq.init(**init_args)

    for n, value in enumerate(itertools.chain(*itertools.repeat(iterable_with_data, times=times_repeat)), 1):
        loop_enable = True
        while loop_enable:
            try:
                qq.put("[{}]: {}".format(n, value), timeout=1)
                loop_enable = False
            except queue.Full:
                if _is_parent_process_killed():
                    logging.debug("[GETTER PARENT KILLED (TERMINATE) -> ppid:{} | pid:{}]".format(os.getppid(),
                                                                                                  os.getpid()))
                    exit()

    logging.debug("[LOOP GETTER STOP -> ppid:{} | pid:{}]".format(os.getppid(), os.getpid()))

    qq.end()
    proxy_end_event.set()
    gc.collect()
    logging.debug("[END GETTER -> ppid:{} | pid:{}]".format(os.getppid(), os.getpid()))



if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging_level)


    qq = QQueue(queue_max_size,
                max_size_bucket_list=None,
                min_size_bucket_list=10,
                logging_level=logging.DEBUG)

    proxy_end_event = multiprocessing.Event()
    proxy_end_event.clear()

    proxy_start_event = multiprocessing.Event()
    proxy_start_event.clear()
    print("ROOT start 2 =================================")
    process = multiprocessing.Process(target=_mprocess, args=(qq,
                                                              qq.get_init_args(),
                                                              proxy_start_event,
                                                              proxy_end_event,
                                                              logging_level))
    process.daemon = True
    process.start()

    start = datetime.now()
    print("ROOT start loop: {}".format(start))
    proxy_start_event.set()

    times_waiting = 0
    loop_enable = True
    while loop_enable:
        try:
            value = qq.get(timeout=0.1)
            # TODO print("VALUE IN PROCESS: {}".format(value))
        except queue.Empty:
            loop_enable = not (proxy_end_event.is_set() and qq.empty())
            if loop_enable:
                times_waiting += 1
                if proxy_start_event.is_set():
                    time_to_retry = 0.1 * times_waiting
                    gc.collect()
                    time.sleep(time_to_retry)
                else:
                    logging.debug("[ROOTG WAIT GETTER -> ppid:{} | pid:{}]".format(os.getppid(),
                                                                                   os.getpid()))
                    gc.collect()
                    proxy_start_event.wait()
                    logging.debug("[ROOTG RESUME WAIT -> ppid:{} | pid:{}]".format(os.getppid(),
                                                                                   os.getpid()))

    if process.is_alive():
        logging.debug("[ROOTG FORCE TO TERMINATE LIVE CHILD -> ppid:{} | pid:{}]".format(os.getppid(),
                                                                                         os.getpid()))
        process.terminate()

    logging.debug("[ROOTG LOOP STOP -> ppid:{} | pid:{}]".format(os.getppid(),
                                                                 os.getpid()))


    finish = datetime.now()
    print("[ROOT ending] finish: {} | diff finish-start: {}".format(finish, finish-start))

    print("ROOT join =================================")
    proxy_end_event.set()
    process.join()
    qq.close()
    print("ROOT end =================================")
