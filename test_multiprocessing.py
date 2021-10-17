import logging
import os
import time
from argparse import ArgumentParser
from collections import OrderedDict
from functools import wraps
from multiprocessing import cpu_count, Pool, Process, Queue
from operator import itemgetter
from zipfile import ZipFile


def timeit(func):
    """
    Decorate function to count executon time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        result_time = time.time() - start_time
        logging.info('--- %s seconds ---', result_time)
        return result
    return wrapper


class Unarchiving(object):
    """
    Test python multiprocessing for files unarchiving.

    Use 3 approches:
     * Pool Map
     * Queue
     * Ordered queue

    There are 2 types of processing:
     * map
     * queue
    
    There are 2 types of queues:
     * simple
     * ordered
    """

    def __init__(self, dir_name, output_dir_name):
        self.process_count = cpu_count()
        self.dir_name = dir_name
        self.output_dir_name = output_dir_name
        self.inputqueue = None
        self.processing_failed = None

    def unarchive(self, filename):
        """
        Unzip file.

        Params:
         * filename - archived file's name
        """
        with ZipFile(filename, 'r') as zip:
            zip.extractall(self.output_dir_name)

    def process_queue(self):
        """
        Unzip files in queue.
        """
        while not self.inputqueue.empty():
            filename = self.inputqueue.get()
            try:
                self.unarchive(filename)
            except Exception as e:
                self._clear_queue()
                self.processing_failed.put(e)

    def set_input_queue(self):
        """
        Prepeare simple queue.

        Returns:
         * Queue - simple queue
        """
        for root, _, files in os.walk(self.dir_name):
            for filename in files:
                self.inputqueue.put(os.path.join(root, filename))
        return self.inputqueue

    def set_ordered_input_queue(self):
        """
        Prepeare ordered queue.
        Approach more efficient than simple queue for unarchiving.

        Returns:
         * Queue - ordered queue
        """
        paths = {}
        for root, _, files in os.walk(self.dir_name):
            for filename in files:
                path = os.path.join(root, filename)
                size = os.path.getsize(path)
                paths[path] = size

        paths = OrderedDict(sorted(
            paths.items(),
            key=itemgetter(1),
            reverse=True,
        ))

        for path in paths:
            self.inputqueue.put(path)
        return self.inputqueue

    def process_using_map(self, *args, **kwargs):
        """
        Proocess files using map approach.

        Params:
         * args - args
         * kwargs - kwargs
        """
        paths = []
        for root, _, files in os.walk(self.dir_name):
            for filename in files:
                paths.append(os.path.join(root, filename))

        with Pool(self.process_count) as pool:
            pool.map(self.unarchive, paths)

    def process_using_queue(self, *args, **kwargs):
        """
        Proocess files using queue approaches.

        Params:
         * args - args
         * kwargs - kwargs
        """
        queue_type = kwargs.get('queue_type')
        queue_types_functions = {
            'simple': self.set_input_queue,
            'ordered': self.set_ordered_input_queue,
        }
        self.inputqueue = Queue()
        self.processing_failed = Queue()
        set_queue = queue_types_functions.get(queue_type)
        self.inputqueue = set_queue()
        producers = [
            Process(
                target=self.process_queue,
                args=(),
            ) for _ in range(self.process_count)
        ]

        for process in producers:
            process.start()

        for process in producers:
            process.join()
        
        if not self.processing_failed.empty():
            raise Exception(self.processing_failed.get())

    @timeit
    def run(self, ttype, *args, **kwargs):
        """
        Run processing.

        Params:
         * ttype - processing approach: map or queue
         * args - args
         * kwargs - kwargs
        """
        types_process_functions = {
            'map': self.process_using_map,
            'queue': self.process_using_queue,
        }
        process = types_process_functions.get(ttype)
        process(*args, **kwargs)

    def _clear_queue(self):
        """
        Clear input queue.

        There are 2 ways to clear multiprocessing queue:
        1) get items from queue while it's not empty;
        2) assign new queue to queue variable.

        2 option is chosen.
        """
        self.inputqueue = Queue()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--source', dest='dir_name', required=True)
    parser.add_argument('-d', '--destination', dest='output_dir_name', required=True)
    parser.add_argument('-t', '--type', dest='type', required=True)
    parser.add_argument('-qt', '--queue_type', dest='queue_type')
    args = parser.parse_args()

    unarchiving = Unarchiving(args.dir_name, args.output_dir_name)
    unarchiving.run(args.type, queue_type=args.queue_type)
