#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import multiprocessing

from quick_queue.quick_queue import QJoinableQueue

try:
    import queue
except ImportError:
    # python 3.x
    import Queue as queue


"""
Execute this script to see result in console

Add two iterables to QJoinableQueue
"""

iterable = range(1, 10001)
iterable2 = range(20000, 21001)


def _process(qjq):
    while True:
        try:
            val = qjq.get(timeout=5.0)
            print(val)
            qjq.task_done()
        except queue.Empty:
            break


if __name__ == "__main__":

    qjq = QJoinableQueue()

    p = multiprocessing.Process(target=_process, args=(qjq,))
    p.start()

    qjq.put_iterable(iterable)

    qjq.put_iterable(iterable2)

    qjq.join()
    print('All work completed')

    p.join()

    print('Process completed')
