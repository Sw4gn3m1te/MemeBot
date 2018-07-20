import queue
import commands
from threading import Thread


class CommandQueue:

    def __init__(self):

        self.priority_queue = queue.Queue()
        self.normal_queue = queue.Queue()
        self.next_command = None

        t = Thread(target=self.get_next_command)
        t.start()

    def add_to_priority_queue(self, req_dict):
        self.priority_queue.put(req_dict)

    def add_to_normal_queue(self, req_dict):
        self.normal_queue.put(req_dict)

    def get_next_command(self):
        while True:
            if self.priority_queue.qsize() > 0:
                self.next_command = self.priority_queue.get()
            else:
                try:
                    self.next_command = self.normal_queue.get()
                except queue.Empty:
                    self.next_command = None
                    pass
