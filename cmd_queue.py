import queue
import commands


class CommandQueue:

    def __init__(self):

        self.priority_queue = queue.Queue()
        self.normal_queue = queue.Queue()
        self.next_command = None

    def add_to_priority_queue(self, req_dict):
        self.priority_queue.put(req_dict)

    def add_to_normal_queue(self, req_dict):
        self.normal_queue.put(req_dict)

    def get_next_command(self):
        if self.priority_queue.qsize() > 0:
            return self.priority_queue.get()
        elif self.normal_queue.qsize() > 0:
            return self.normal_queue.get()
        else:
            return None

    def clear_queues(self):
        self.normal_queue.queue.clear()
        self.priority_queue.queue.clear()




