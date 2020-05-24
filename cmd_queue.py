import queue
import commands
import json


class CommandQueue:

    @commands.exception_logger
    def __init__(self):
        self.priority_queue = queue.Queue()
        self.normal_queue = queue.Queue()
        self.next_command = None
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    @commands.exception_logger
    def add_to_priority_queue(self, req_dict):
        self.priority_queue.put(req_dict)

    @commands.exception_logger
    def add_to_normal_queue(self, req_dict):
        self.normal_queue.put(req_dict)

    @commands.exception_logger
    def get_next_command(self):
        if self.priority_queue.qsize() > 0:
            return self.priority_queue.get()
        elif self.normal_queue.qsize() > 0:
            return self.normal_queue.get()
        else:
            return None

    @commands.exception_logger
    def clear_queues(self):
        keep_normal = []
        keep_prio = []
        while self.normal_queue.qsize() > 0:
            req_dict = self.normal_queue.get()
            if req_dict['cmd']['name'] in self.config['NonStop'].keys():
                keep_normal.append(req_dict)
        while self.priority_queue.qsize() > 0:
            req_dict = self.normal_queue.get()
            if req_dict['cmd']['name'] in self.config['NonStop'].keys():
                keep_prio.append(req_dict)

        self.normal_queue.queue.clear()
        self.priority_queue.queue.clear()

        for r in keep_normal:
            self.add_to_normal_queue(r)
        for r in keep_prio:
            self.add_to_priority_queue(r)




