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
times_repeat = 1000000
logging_level = logging.DEBUG


def _is_parent_process_killed():
    """
    Return if parent process was killed
    :return: True if parent process was killed
    """
    return os.getppid() == 1


def _mprocess(qq,
              proxy_start_event,
              proxy_end_event,
              logging_level):
    logging.basicConfig(stream=sys.stderr, level=logging_level)
    ipid = -1

    logging.debug("[START -> id:{} | ppid:{} | pid:{}]".format(ipid, os.getppid(), os.getpid()))

    times_waiting = 0

    loop_enable = True
    while loop_enable:
        try:
            _ = qq.get(timeout=0.1)
            # TODO print("VALUE IN PROCESS: {}".format(value))

            times_waiting = 0

        except queue.Empty:
            loop_enable = not (proxy_end_event.is_set() and qq.empty())
            if loop_enable:
                times_waiting += 1
                if proxy_start_event.is_set():
                    time_to_retry = 0.1 * times_waiting

                    if _is_parent_process_killed():
                        logging.debug("[PARENT KILLED (TERMINATE) -> "
                                      "id:{} | ppid:{} | pid:{}]".format(ipid,
                                                                         os.getppid(),
                                                                         os.getpid()))
                        loop_enable = False
                    else:
                        gc.collect()
                        time.sleep(time_to_retry)
                else:
                    logging.debug("[WAIT -> id:{} | ppid:{} | pid:{}]".format(ipid,
                                                                              os.getppid(),
                                                                              os.getpid()))
                    gc.collect()
                    proxy_start_event.wait()

                    logging.debug("[RESUME WAIT -> id:{} | ppid:{} | pid:{}]".format(ipid,
                                                                                     os.getppid(),
                                                                                     os.getpid()))
        except Exception as err:
            logging.error("[ERROR -> id:{} | ppid:{} | pid:{}]: {}".format(ipid, os.getppid(), os.getpid(), err))
            raise

    logging.debug("[LOOP STOP -> id:{} | ppid:{} | pid:{}]".format(ipid, os.getppid(), os.getpid()))
    gc.collect()

    logging.debug("[END -> id:{} | ppid:{} | pid:{}]".format(ipid, os.getppid(), os.getpid()))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging_level)

    queue_max_size = 1000
    qq = QQueue(queue_max_size,
                max_size_bucket_list=None,
                min_size_bucket_list=10,
                logging_level=logging.DEBUG)

    proxy_end_event = multiprocessing.Event()
    proxy_end_event.clear()

    proxy_start_event = multiprocessing.Event()
    proxy_start_event.clear()
    print("ROOT start =================================")
    process = multiprocessing.Process(target=_mprocess, args=(qq,
                                                              proxy_start_event,
                                                              proxy_end_event,
                                                              logging_level))
    process.daemon = True
    process.start()

    start = datetime.now()
    print("ROOT start loop: {}".format(start))
    proxy_start_event.set()
    n = 0
    for n, value in enumerate(itertools.chain(*itertools.repeat(iterable_with_data, times=times_repeat)), 1):
        qq.put("[{}]: {}".format(n, value))
    qq.end()

    finish = datetime.now()
    print("[ROOT ending] finish: {} | diff finish-start: {}".format(finish, finish-start))

    print("ROOT join ================================= n: {}".format(n))
    proxy_end_event.set()
    process.join()
    qq.close()
    print("ROOT end =================================")
