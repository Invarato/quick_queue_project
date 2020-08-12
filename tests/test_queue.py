# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import gc
import logging
import multiprocessing
import os
import sys
import time

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
] * 1000
logging_level = logging.DEBUG


def _is_parent_process_killed():
    """
    Return if parent process was killed
    :return: True if parent process was killed
    """
    return os.getppid() == 1


def _mprocess(proxy_queue,
              logging_level):
    # logging.basicConfig(stream=sys.stderr, level=logging_level)
    ipid = -1

    # logging.debug("[START -> id:{} | ppid:{} | pid:{}]".format(ipid, os.getppid(), os.getpid()))

    def fun_get_value(value):
        print("VALUE IN PROCESS: {}".format(value))

    proxy_queue.getter_loop(fun_get_value, ipid)



if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging_level)

    queue_max_size = 1000
    proxy_queue = QQueue(queue_max_size)

    proxy_end_event = multiprocessing.Event()
    proxy_end_event.clear()

    proxy_start_event = multiprocessing.Event()
    proxy_start_event.clear()
    print("ROOT empezar =================================")
    process = multiprocessing.Process(target=_mprocess, args=(proxy_queue,
                                                              logging_level))
    process.daemon = True
    process.start()

    print("ROOT enviar =================================")
    proxy_start_event.set()
    n = 0
    for n, value in enumerate(iterable_with_data, 1):
        proxy_queue.put("[{}]: {}".format(n, value))
    proxy_queue.end()

    print("ROOT terminando ================================= n: {}".format(n))
    proxy_end_event.set()
    process.join()
    print("ROOT terminar =================================")
