# -*- coding: utf-8 -*-
#
# @autor: Ramón Invarato Menéndez
# @version 1.7
import logging
import multiprocessing.context
import multiprocessing.queues
import sys

try:
    import queue
except ImportError:
    # python 3.x
    import Queue as queue


__test__ = {'import_test': """
                           >>> from quick_queue.quick_queue import QQueue, QJoinableQueue
                           >>> import multiprocessing
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


def QJoinableQueue(*args, **kwargs):
    """
    This method return one instance of QuickJoinableQueue.

    It is importan the size of list (named here "bucket list") in relation productor and consumers process to have
    the best performance. If queue is full, mean consumers are slower than productor; on the other hand, if
    queue is empty, mean productor is slower than consumers. Then, best size of bucket list (size_bucket_list) is
    where queue is not full and not empty. Here, I implemented one sensor to determinate in realtime the
    size_bucket_list, you can enable this sensor if size_bucket_list is None (if you define a size_bucket_list
    number, then you want a constant value to size_bucket_list); by default is enable the sensor
    (size_bucket_list=None), because depend on Hardware in your computer this value should change, I recommend
    you test the best performance for your computer modifying size_bucket_list (None and with number value).

    Example of use (about doctest: Process not work in doctest, you can try this example in
    test/test_joinablequeue_simple.py):
    >>> def _process(qjq):
    ...     print(qjq.get())
    ...     print(qjq.get())
    ...     print(qjq.get())
    ...     qjq.task_done()
    >>> qjq = QJoinableQueue()
    >>> p = multiprocessing.Process(target=_process, args=(qjq,))
    >>> p.start()
    >>> qjq.put("A")
    >>> qjq.put("B")
    >>> qjq.put("C")
    >>> qjq.join()
    >>> p.join()

    Note: end() method close and put data remain. If you only want put data remain (no close queue)
    use put_remain()

    Example with iterable (about doctest: Process not work in doctest, you can try one example similar in
    test/test_joinablequeue_iterable.py):
    >> def _process(qjq):
    ...     print(qjq.get())
    ...     print(qjq.get())
    ...     print(qjq.get())
    >>> qjq = QJoinableQueue()
    >>> p = multiprocessing.Process(target=_process, args=(qjq,))
    >>> p.start()
    >>> qjq.put_iterable(["A", "B", "C"])
    >>> qjq.join()
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
    return QuickJoinableQueue(*args, **kwargs)


class QuickQueue(multiprocessing.queues.Queue):

    def __init__(self,
                 maxsize=1000,
                 size_bucket_list=None,
                 min_size_bucket_list=10,
                 max_size_bucket_list=None,
                 logging_level=logging.WARNING,
                 ctx=None):
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
                                     Min == 1 and max == max_size_bucket_list - 1 (other wise, this raise a ValueError).
                                     By default: 10
        :param max_size_bucket_list: (only if sensor is enabled) max size bucket list. If None is infinite.
                                     By defatult: None
        :raise ValueError: if min_size_bucket_list is not: 1 < min_size_bucket_list <= max_size_bucket_list - 1
        """
        multiprocessing.queues.Queue.__init__(self, maxsize, ctx=multiprocessing.get_context() if ctx is None else ctx)

        self.enable_sensor = None
        self.size_bucket_list = None
        self.bucket_getting = None
        self.bucket_list = None

        self.c_max_size = None
        self.half_max_size = None

        self.def_max_size_bucket_list = None
        self.max_size_bucket_list = None
        self.half_max_size_bucket_list = None

        self.min_size_bucket_list = None
        self.min_size_bucket_list_plusone = None

        self.wait_check = None

        self.change_quick = None
        self.prev_stable = None

        self.determinate_max = None
        self.max_qsize_determinate_max = None
        self.cache_size_bucket_list = None
        self.set_values = None
        self.touch_min_size_bucket_list = None
        self.touch_max_size_bucket_list = None

        self.init_args = {'maxsize': maxsize,
                          'size_bucket_list': size_bucket_list,
                          'min_size_bucket_list': min_size_bucket_list,
                          'max_size_bucket_list': max_size_bucket_list,
                          'logging_level': logging_level}

        self.init(**self.init_args)

    def get_init_args(self):
        """
        This return initial args.

        :return: return a dict with your args
        """
        return self.init_args

    def init(self,
             maxsize=1000,
             size_bucket_list=None,
             min_size_bucket_list=10,
             max_size_bucket_list=None,
             logging_level=logging.WARNING):
        """
        Initialization in each process.

        :param maxsize: maxsize of buckets in queue. If maxsize<=0 then queue is infinite (and sensor is disabled).
                        By default: 1000
        :param size_bucket_list: None to enable sensor size bucket list (require maxsize>0). If a number is defined
                                 here then use this number to size_bucket_list and disable sensor. If maxsize<=0
                                 and size_bucket_list==None then size_bucket_list is default to 1000; other wise,
                                 if maxsize<=0 and size_bucket_list is defined, then use this number. By default: None
        :param min_size_bucket_list: (only if sensor is enabled) min size bucket list.
                                     Min == 1 and max == max_size_bucket_list - 1 (other wise, this raise a ValueError).
                                     By default: 10
        :param max_size_bucket_list: (only if sensor is enabled) max size bucket list. If None is infinite.
                                     By defatult: None
        :param logging_level: logging level. By default: logging.WARNING
        :raise ValueError: if min_size_bucket_list is not: 1 < min_size_bucket_list <= max_size_bucket_list - 1
        :return:
        """

        logging.basicConfig(stream=sys.stderr, level=logging_level)
        if maxsize and maxsize > 0:
            self.enable_sensor = not bool(size_bucket_list)
            self.size_bucket_list = size_bucket_list if size_bucket_list else 10
        else:
            self.enable_sensor = False
            self.size_bucket_list = size_bucket_list if size_bucket_list else 1000

        logging.debug("[QQUEUE - SENSOR INIT]: enable_sensor={} | "
                      "size_bucket_list={}".format(self.enable_sensor,
                                                   self.size_bucket_list))

        self.bucket_getting = list()
        self.bucket_list = list()

        self.c_max_size = maxsize if maxsize else 100000
        self.half_max_size = self.c_max_size // 2

        self.def_max_size_bucket_list = max_size_bucket_list
        if max_size_bucket_list:
            self.max_size_bucket_list = self.def_max_size_bucket_list
            self.half_max_size_bucket_list = self.max_size_bucket_list / 2
        else:
            self.max_size_bucket_list = 10000
            self.half_max_size_bucket_list = self.max_size_bucket_list / 2

        if min_size_bucket_list < 1 or min_size_bucket_list > self.max_size_bucket_list - 1:
            raise ValueError("min_size_bucket_list={} but range permitted: "
                             "1 < min_size_bucket_list <= max_size_bucket_list - 1".format(min_size_bucket_list))

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
            if new_size_bucket_list < self.min_size_bucket_list:
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
                if qsize < self.max_qsize_determinate_max or \
                        (self.def_max_size_bucket_list and self.size_bucket_list > self.def_max_size_bucket_list):
                    self.determinate_max = False
                    if self.def_max_size_bucket_list:
                        self.max_size_bucket_list = min(self.def_max_size_bucket_list, self.def_max_size_bucket_list)
                    else:
                        self.max_size_bucket_list = self.size_bucket_list

                    self.half_max_size_bucket_list = self.max_size_bucket_list / 2
                    self.max_qsize_determinate_max = 0

                    if self.size_bucket_list > self.max_size_bucket_list:
                        self.size_bucket_list = self.max_size_bucket_list

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
                            self.half_max_size_bucket_list = self.max_size_bucket_list / 2
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

    def put_bucket(self, bucket, *args, **kwargs):
        """
        This put in queue a list of data

        :param bucket: list of individual data
        :param args: args to put queue method
        :return:
        """
        super().put(bucket, *args, **kwargs)

    def put(self, value, *args, **kwargs):
        """
        This put in queue a data wrapped in a list. Accumulate data until size_bucket_list, then put in queue.

        In the end all put all, call to put_remain() to ensure enqueue all buckets.

        Note: If you put in other process different where QQueue was instanced, then you should be call to init()
        method prior to put. In other case, default values will load in other process instance by default.

        :param value: individual value to enqueue
        :param args: args to put queue method
        :return:
        """
        try:
            self.bucket_list.append(value)

            if len(self.bucket_list) > self.size_bucket_list:
                self.put_bucket(self.bucket_list, *args, **kwargs)
                self.bucket_list = list()

                if self.enable_sensor:
                    self._sensor_size_list()
        except AttributeError:
            self.init(maxsize=1000,
                      size_bucket_list=None,
                      min_size_bucket_list=10,
                      max_size_bucket_list=None,
                      logging_level=logging.WARNING)
            self.bucket_list = [value]

    def put_remain(self, *args, **kwargs):
        """
        Call to enqueue rest values that remains

        :param args: args to put queue method
        :return:
        """
        if self.bucket_list:
            self.put_bucket(self.bucket_list, *args, **kwargs)
            self.bucket_list = list()

    def put_iterable(self, iterable, *args, **kwargs):
        """
        This put in this QQueue all data from an iterable.

        If you use this method you do not need to call to put_remain (it is called in the end of iterable).

        This method not call to close queue (you can use several times this method with multiples iterables).

        :param iterable: iterable of values to enqueue (individually)
        :param args: args to put queue method
        :return:
        """
        for v in iterable:
            self.put(v, *args, **kwargs)

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


class QuickJoinableQueue(QuickQueue,
                         multiprocessing.queues.JoinableQueue):

    def __init__(self,
                 maxsize=1000,
                 size_bucket_list=None,
                 min_size_bucket_list=10,
                 max_size_bucket_list=None,
                 logging_level=logging.WARNING,
                 ctx=None):
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
                                     Min == 1 and max == max_size_bucket_list - 1 (other wise, this raise a ValueError).
                                     By default: 10
        :param max_size_bucket_list: (only if sensor is enabled) max size bucket list. If None is infinite.
                                     By defatult: None
        :raise ValueError: if min_size_bucket_list is not: 1 < min_size_bucket_list <= max_size_bucket_list - 1
        """
        self._ctx = multiprocessing.get_context() if ctx is None else ctx
        QuickQueue.__init__(self,
                            maxsize=maxsize,
                            size_bucket_list=size_bucket_list,
                            min_size_bucket_list=min_size_bucket_list,
                            max_size_bucket_list=max_size_bucket_list,
                            logging_level=logging_level,
                            ctx=self._ctx)
        multiprocessing.queues.JoinableQueue.__init__(self, maxsize, ctx=self._ctx)

    def put_bucket(self, bucket, block=True, timeout=None):
        """
        This put in queue a list of data

        :param bucket: list of individual data
        :param block: optional args block is true and timeout is None (the default), block if necessary until a free
        slot is available.
        :param timeout: If timeout is a positive number, it blocks at most timeout seconds and raises the Full exception
        if no free slot was available within that time. Otherwise (block is false), put an item on the queue if a free
        slot is immediately available, else raise the Full exception (timeout is ignored in that case).
        :return:
        """

        if self._closed:
            raise ValueError(f"Queue {self!r} is closed")
        if not self._sem.acquire(block, timeout):
            raise queue.Full

        with self._notempty, self._cond:
            if self._thread is None:
                self._start_thread()

            c = len(bucket)
            self._buffer.append(bucket)

            for _ in range(c):
                self._unfinished_tasks.release()

            self._notempty.notify()

    def join(self):
        """
        Blocks until all items in the queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the queue.
        The count goes down whenever a consumer thread calls task_done() to indicate
        that the item was retrieved and all work on it is complete. When the count of
        unfinished tasks drops to zero, join() unblocks.
        :return:
        """
        QuickQueue.put_remain(self)
        multiprocessing.queues.JoinableQueue.join(self)

    def end(self):
        """
        Do not use end method with QuickJoinableQueue.
        Use join or put_remain instead.
        You need call to close method if you need it.
        :return:
        """
        QuickQueue.put_remain(self)
        raise Warning("With QuickJoinableQueue use join() or put_remain()")
