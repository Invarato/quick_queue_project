# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.0
import logging
import multiprocessing.context
import multiprocessing.queues
import sys


__test__ = {'import_test': """
                           >>> from sorted_in_disk.quick_queue import *

                           """
            }


def QQueue(*args, **kwargs):
    """
    This method return one instance of QuickQueue.

    It is importan the size of list (named here "bucket list") in relation productor and consumers process to have
    the best performance. If queue is full, mean consumers are slower than productor; on the other hand, if
    queue is empty, mean productor is slower than consumers. Then, best size of bucket list (size_bucket_list) is
    where queue is not full and not empty. Here, I implemented one sensor to determinate in realtime the
    size_bucket_list, you can enable this sensor if size_bucket_list is None (if you define a size_bucket_list
    number, then you want a constant value to size_bucket_list); by default is enable the sensor
    (size_bucket_list=None), because depend on Hardware in your computer this value should change, I recommend
    you test the best performance for your computer modifying size_bucket_list (None and with number value).

    Example of use (about doctest: Process not work in doctest, you can try this example in
    test/test_queue_simple.py):
    >>> def _process(qq):
    ...     print(qq.get())
    ...     print(qq.get())
    ...     print(qq.get())
    >>> qq = QQueue()
    >>> p = multiprocessing.Process(target=_process, args=(qq,))
    >>> p.start()
    >>> qq.put("A")
    >>> qq.put("B")
    >>> qq.put("C")
    >>> qq.end()
    >>> p.join()

    Note: end() method close and put data remain. If you only want put data remain (no close queue)
    use put_remain()

    Example with iterable (about doctest: Process not work in doctest, you can try one example similar in
    test/test_queue_iterable.py):
    >> def _process(qq):
    ...     print(qq.get())
    ...     print(qq.get())
    ...     print(qq.get())
    >>> qq = QQueue()
    >>> p = multiprocessing.Process(target=_process, args=(qq,))
    >>> p.start()
    >>> qq.put_iterable(["A", "B", "C"])
    >>> qq.end()
    >>> p.join()

    :param maxsize: maxsize of buckets in queue. If maxsize<=0 then queue is infinite (and sensor is disabled).
                    By default: 1000
    :param size_bucket_list: None to enable sensor size bucket list (require maxsize>0). If a number is defined
                             here then use this number to size_bucket_list and disable sensor. If maxsize<=0
                             and size_bucket_list==None then size_bucket_list is default to 1000; other wise,
                             if maxsize<=0 and size_bucket_list is defined, then use this number. By default: None
    :param min_size_bucket_list: (only if sensor is enabled) min size bucket list.
                                 Min == 1 and max == max_size_bucket_list - 1. By default: 10
    :param max_size_bucket_list: (only if sensor is enabled) max size bucket list. If None is infinite.
                                 By defatult: None
    """
    return QuickQueue(*args, **kwargs)


class QuickQueue(multiprocessing.queues.Queue):

    def __init__(self,
                 maxsize=1000,
                 size_bucket_list=None,
                 min_size_bucket_list=10,
                 max_size_bucket_list=None,
                 logging_level=logging.WARNING):
        """
        This class is a data wrapper into list structure to put in multiprocess queue and
        to accelerate enqueue and dequeue.

        Multiprocess queue is pretty slow putting and getting individual data, then this class wrap several data in
        a list, this list is one single data that is enqueue in queue than is more quickly than put one individual data.

        :param maxsize: maxsize of buckets in queue. If maxsize<=0 then queue is infinite (and sensor is disabled).
                        By default: 1000
        :param size_bucket_list: None to enable sensor size bucket list (require maxsize>0). If a number is defined
                                 here then use this number to size_bucket_list and disable sensor. If maxsize<=0
                                 and size_bucket_list==None then size_bucket_list is default to 1000; other wise,
                                 if maxsize<=0 and size_bucket_list is defined, then use this number. By default: None
        :param min_size_bucket_list: (only if sensor is enabled) min size bucket list.
                                     Min == 1 and max == max_size_bucket_list - 1. By default: 10
        :param max_size_bucket_list: (only if sensor is enabled) max size bucket list. If None is infinite.
                                     By defatult: None
        """
        super(QuickQueue, self).__init__(maxsize, ctx=multiprocessing.get_context())
        logging.basicConfig(stream=sys.stderr, level=logging_level)

        if maxsize and maxsize > 0:
            self.enable_sensor = not bool(size_bucket_list)
            self.size_bucket_list = size_bucket_list if size_bucket_list else 10
        else:
            self.enable_sensor = False
            self.size_bucket_list = size_bucket_list if size_bucket_list else 1000

        self.bucket_getting = list()
        self.bucket_list = list()

        self.c_max_size = maxsize if maxsize else 100000
        self.half_max_size = self.c_max_size // 2

        self.def_max_size_bucket_list = max_size_bucket_list
        if max_size_bucket_list:
            self.max_size_bucket_list = self.def_max_size_bucket_list
            self.half_max_size_bucket_list = self.max_size_bucket_list // 2
        else:
            self.max_size_bucket_list = 10000
            self.half_max_size_bucket_list = self.max_size_bucket_list // 2
        self.min_size_bucket_list = min_size_bucket_list
        self.min_size_bucket_list_plusone = min_size_bucket_list + 1

        self.wait_check = 0

        self.change_quick = 0
        self.prev_stable = self.half_max_size

        self.determinate_max = True
        self.max_qsize_determinate_max = 0
        self.cache_size_bucket_list = dict()
        self.set_values = set()
        self.touch_min_size_bucket_list = 0
        self.touch_max_size_bucket_list = 0

    def _autocalculate_size_bucket_list(self, qsize):
        """
        Helper function to calculate distante new size bucket list relatively to distance to half in relation
        max size. By other hand, this is a cache to return data previously calculated.
        :param qsize: current qsize
        :return: new size bucket list
        """
        try:
            return self.cache_size_bucket_list[qsize]
        except KeyError:
            if qsize < self.half_max_size:
                mult = -1 * (1.0 - qsize / self.half_max_size)
            else:
                mult = (qsize-self.half_max_size) / self.half_max_size

            new_size_bucket_list = int(self.half_max_size_bucket_list + (self.half_max_size_bucket_list * mult))
            if new_size_bucket_list < self.min_size_bucket_list_plusone:
                new_size_bucket_list = self.min_size_bucket_list

            self.cache_size_bucket_list[qsize] = new_size_bucket_list
            return new_size_bucket_list

    def _sensor_size_list(self):
        """
        Sensor to determinate in realtime the size bucket list.

        :return:
        """
        if self.wait_check > 0:
            self.wait_check -= 1
        else:
            qsize = self.qsize()
            if self.determinate_max:
                self.size_bucket_list += 100
                if qsize < self.max_qsize_determinate_max:
                    self.determinate_max = False
                    if self.def_max_size_bucket_list:
                        self.max_size_bucket_list = min(self.def_max_size_bucket_list, self.def_max_size_bucket_list)
                    else:
                        self.max_size_bucket_list = self.size_bucket_list

                    self.half_max_size_bucket_list = self.max_size_bucket_list // 2
                    self.max_qsize_determinate_max = 0

                    logging.debug("[QQUEUE - MAX DETERMINATE]: "
                                  "max_size_bucket_list={}".format(self.max_size_bucket_list))
                else:
                    self.max_qsize_determinate_max = qsize
            else:
                self.wait_check = self.c_max_size / 2
                self.size_bucket_list = self._autocalculate_size_bucket_list(qsize)

                if self.size_bucket_list == self.min_size_bucket_list:
                    self.touch_min_size_bucket_list += 1
                    self.touch_max_size_bucket_list = 0
                    if self.touch_min_size_bucket_list > 5:
                        # Reducing max_size_bucket_list for overflow
                        if self.set_values:
                            self.max_size_bucket_list = (max(self.set_values) + self.max_size_bucket_list) // 2
                            self.set_values = set()
                            self.touch_min_size_bucket_list = 0
                            self.half_max_size_bucket_list = self.max_size_bucket_list // 2
                            self.cache_size_bucket_list = {}
                            logging.debug("[QQUEUE - OVERFLOW BELOW]: "
                                          "max_size_bucket_list={}".format(self.max_size_bucket_list))
                        else:
                            self.touch_min_size_bucket_list = 0
                            self.determinate_max = True
                elif self.size_bucket_list == self.max_size_bucket_list:
                    self.touch_max_size_bucket_list += 1
                    self.touch_min_size_bucket_list = 0
                    if self.touch_max_size_bucket_list > 5:
                        logging.debug("[QQUEUE - OVERFLOW ABOVE]: "
                                      "max_size_bucket_list={}".format(self.max_size_bucket_list))
                        self.determinate_max = True
                        self.touch_max_size_bucket_list = 0
                else:
                    self.set_values.add(self.size_bucket_list)

            logging.debug("[QQUEUE - NEW DATA DETERMINATED]: qsize={} | "
                          "size_bucket_list={}".format(qsize,
                                                       self.size_bucket_list))

    def put_bucket(self, bucket, *args):
        """
        This put in queue a list of data

        :param bucket: list of individual data
        :param args: args to put queue method
        :return:
        """
        super().put(bucket, *args)

    def put(self, value, *args):
        """
        This put in queue a data wrapped in a list. Accumulate data until size_bucket_list, then put in queue.

        In the end all put all, call to put_remain() to ensure enqueue all buckets

        :param value: individual value to enqueue
        :param args: args to put queue method
        :return:
        """
        try:
            self.bucket_list.append(value)

            if len(self.bucket_list) > self.size_bucket_list:
                self.put_bucket(self.bucket_list, *args)
                self.bucket_list = list()

                if self.enable_sensor:
                    self._sensor_size_list()
        except AttributeError:
            self.put_bucket([value], *args)

    def put_remain(self, *args):
        """
        Call to enqueue rest values that remains

        :param args: args to put queue method
        :return:
        """
        if self.bucket_list:
            self.put_bucket(self.bucket_list, *args)
            del self.bucket_list

    def put_iterable(self, iterable, *args):
        """
        This put in this QQueue all data from an iterable.

        If you use this method you do not need to call to put_remain (it is called in the end of iterable).

        This method not call to close queue (you can use several times this method with multiples iterables).

        :param iterable: iterable of values to enqueue (individually)
        :param args: args to put queue method
        :return:
        """
        for v in iterable:
            self.put(v, *args)

        self.put_remain()

    def end(self):
        """
        Helper to call to put_remain and close queue in one method
        :return:
        """
        self.put_remain()
        self.close()

    def get_bucket(self, *args, **kwargs):
        """
        This get from queue a list of data

        :param args: args to get queue method
        :param kwargs: kwargs to get queue method
        :return:
        """
        return super().get(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        This get from queue a data unwrapped from the list.

        To prevent miss data, you need to call get until end of queue; if you think in terminate premature a consumer,
        then it is best call get_bucket to obtain a list of data and iterate until end.

        :param args: args to get queue method
        :param kwargs: kwargs to get queue method
        :return:
        """
        try:
            return self.bucket_getting.pop(0)
        except IndexError:
            self.bucket_getting = self.get_bucket(*args, **kwargs)
            return self.get(*args, **kwargs)
        except AttributeError:
            self.bucket_getting = self.get_bucket(*args, **kwargs)
            return self.get(*args, **kwargs)
