# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import multiprocessing

from quick_queue.quick_queue import QQueue

"""
Execute this script to see result in console

Add some values to qqueue
"""


def _process(qq):
    print(qq.get())
    print(qq.get())
    print(qq.get())


if __name__ == "__main__":

    qq = QQueue()

    p = multiprocessing.Process(target=_process, args=(qq,))
    p.start()

    qq.put("A")
    qq.put("B")
    qq.put("C")

    qq.end()

    p.join()
