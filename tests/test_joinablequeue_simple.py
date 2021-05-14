#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import multiprocessing

from quick_queue.quick_queue import QJoinableQueue

"""
Execute this script to see result in console

Add some values to QJoinableQueue
"""


def _process(qjq):
    print(qjq.get())
    qjq.task_done()

    print(qjq.get())
    qjq.task_done()

    print(qjq.get())
    qjq.task_done()


if __name__ == "__main__":

    qjq = QJoinableQueue()

    p = multiprocessing.Process(target=_process, args=(qjq,))
    p.start()

    qjq.put("A")
    qjq.put("B")
    qjq.put("C")

    print('All task requests sent\n', end='')

    # block until all tasks are done
    qjq.join()
    print('All work completed')

    p.join()
    print('Process completed')
