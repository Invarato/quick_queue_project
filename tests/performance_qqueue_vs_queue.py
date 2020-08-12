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
from multiprocessing import Queue

"""
Execute this script to see result in console

Compare in your system the performance of QuickQueue vs Multiprocessing.Queue

:param count_elements: generate more elements to test in a range method
"""
count_elements = 1000000


def _process(q_qq):
    start = datetime.now()
    print("[PROCESS START]: {}".format(start))
    for _ in range(1, count_elements):
        __ = q_qq.get()
    finish = datetime.now()
    print("[PROCESS END] finish: {} | diff finish-start: {}".format(finish, finish-start))


if __name__ == "__main__":

    print("========================= VELOCITY TEST IN QUICK QUEUE =========================")

    start = datetime.now()
    print("[ROOT START]: {}".format(start))
    qq = QQueue(1000)

    p = multiprocessing.Process(target=_process, args=(qq,))
    p.start()

    for num in range(1, count_elements):
        qq.put(num)

    qq.end()

    p.join()

    finish = datetime.now()
    diff1 = finish-start
    print("[ROOT END] finish: {} | diff finish-start: {}".format(finish, diff1))

    print("========================= VELOCITY TEST IN NORMAL QUEUE =========================")

    start = datetime.now()
    print("[ROOT START]: {}".format(start))
    q = Queue()

    p = multiprocessing.Process(target=_process, args=(q,))
    p.start()

    for num in range(1, count_elements):
        q.put(num)

    q.close()

    p.join()

    finish = datetime.now()
    diff2 = finish-start
    print("[ROOT END] finish: {} | diff finish-start: {}".format(finish, diff2))

    print("[ROOT COMPARE] diff QuickQueue: {} | diff Queue: {}".format(diff1, diff2))
