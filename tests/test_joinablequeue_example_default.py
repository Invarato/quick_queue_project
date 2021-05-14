#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import threading

from quick_queue.quick_queue import QJoinableQueue

"""
Execute this script to see result in console

Add some values to qJoinQueue

Code example from https://docs.python.org/3/library/queue.html#queue.Queue.join
"""


qjq = QJoinableQueue()

def worker():
    print("Worker")
    while True:
        item = qjq.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        qjq.task_done()


# turn-on the worker thread
threading.Thread(target=worker, daemon=True).start()

# send thirty task requests to the worker
for item in range(30):
    qjq.put(item)
print('All task requests sent\n', end='')

# block until all tasks are done
qjq.join()
print('All work completed')
