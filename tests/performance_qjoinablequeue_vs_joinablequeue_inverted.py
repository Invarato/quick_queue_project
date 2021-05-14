# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import multiprocessing
from datetime import datetime

from quick_queue.quick_queue import QJoinableQueue
from multiprocessing import JoinableQueue

"""
Execute this script to see result in console

Compare in your system the performance of QuickJoinableQueue vs Multiprocessing.JoinableQueue

:param count_elements: generate more elements to test in a range method
"""
count_elements = 1000000


def _process(jq_qjq):
    start = datetime.now()

    try:
        jq_qjq.initialice_in_process(1000)
    except AttributeError:
        pass

    print("[PROCESS START]: {}".format(start))
    for num in range(1, count_elements):
        jq_qjq.put(num)

    jq_qjq.join()

    finish = datetime.now()
    print("[PROCESS END] finish: {} | diff finish-start: {}".format(finish, finish-start))


if __name__ == "__main__":

    print("========================= VELOCITY TEST IN QUICK JOINABLE QUEUE =========================")

    start = datetime.now()
    print("[ROOT START]: {}".format(start))
    qjq = QJoinableQueue(1000)

    p = multiprocessing.Process(target=_process, args=(qjq,))
    p.start()

    for _ in range(1, count_elements):
        __ = qjq.get()
        qjq.task_done()

    p.join()

    qjq.close()

    finish = datetime.now()
    diff1 = finish-start
    print("[ROOT END] finish: {} | diff finish-start: {}".format(finish, diff1))

    print("========================= VELOCITY TEST IN NORMAL JOINABLE QUEUE =========================")

    start = datetime.now()
    print("[ROOT START]: {}".format(start))
    jq = JoinableQueue()

    p = multiprocessing.Process(target=_process, args=(jq,))
    p.start()

    for _ in range(1, count_elements):
        __ = qjq.get()
        jq.task_done()

    p.join()

    jq.close()

    finish = datetime.now()
    diff2 = finish-start
    print("[ROOT END] finish: {} | diff finish-start: {}".format(finish, diff2))
    print("")
    print("[ROOT COMPARE] diff QuickJoinableQueue: {} | diff JoinableQueue: {}".format(diff1, diff2))
