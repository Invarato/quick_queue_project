# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import multiprocessing

from quick_queue.quick_queue import QQueue

try:
    import queue
except ImportError:
    # python 3.x
    import Queue as queue

"""
Execute this script to see result in console

Add two iterables to qqueue
"""
iterable = range(1, 10001)
iterable2 = range(20000, 21001)


def _process(qq):
    while True:
        try:
            val = qq.get(timeout=5.0)
            print(val)
        except queue.Empty:
            break


if __name__ == "__main__":

    qq = QQueue()

    p = multiprocessing.Process(target=_process, args=(qq,))
    p.start()

    qq.put_iterable(iterable)

    qq.put_iterable(iterable2)

    qq.end()

    p.join()
