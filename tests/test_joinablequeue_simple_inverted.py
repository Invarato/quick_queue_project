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
    qjq.put("A")
    qjq.put("B")
    qjq.put("C")
    print('All work completed')

    qjq.join()
    print('SubProcess completed')


if __name__ == "__main__":

    qjq = QJoinableQueue()

    p = multiprocessing.Process(target=_process, args=(qjq,))
    p.start()

    print(qjq.get())
    qjq.task_done()

    print(qjq.get())
    qjq.task_done()

    print(qjq.get())
    qjq.task_done()

    print('MainProcess completed')
