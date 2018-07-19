import configparser
import queue

class CommandHandler:

    """
    handles the permissions aswell as the order of the command execution
    """

    def __init__(self, c, event):

        self.c = c
        self.event = event
        self.priority_queue = queue.Queue()
        self.normal_queue = queue.Queue()
        self.repeating_command_list = []
        self.user_permission_level = 2
        self.needed_command_permission_level = 2
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read("config.ini")
        cc = self.config.items("CommandCharacter")
        self.command_character = cc[0][0]

        self.req_dict = self.parse_msg_to_req_dict()


    def parse_msg_to_req_dict(self):

        # {'targetmode': '3', 'msg': '#test', 'invokerid': '2', 'invokername': 'DRAW MONSTA CARDO', 'invokeruid': 'VUIuVaoZpicscTxXuM6kO+7j1hM='}

        req_dict = {}
        msg = str(self.event[0]['msg'])

        invoker_name = str(self.event[0]['invokername'])
        invoker_uid = str(self.event[0]['invokeruid'])
        invoker_clid = str(self.event[0]['invokerid'])


        msg = msg[len(self.command_character):]
        arglist = msg.split()
        cmd_name = arglist[0]
        cmd_args = arglist[1:]

        rep_cmd_list = []
        for row in range(len(self.config.items("RepeatingCommands"))):
            rep_cmd_list.append(self.config.items("RepeatingCommands")[row][0])
        repeats = 0
        if cmd_name in rep_cmd_list:
            repeats = cmd_args[1] #2 arg aus cmd args

        req_dict = {"invoker": {"name": invoker_name, "uid": invoker_uid, "clid": invoker_clid},
                    "cmd": {"name": cmd_name, "args": cmd_args, "repeats": repeats}, "event": self.event}

        print(req_dict)

        return req_dict


    def check_permission(self, req_dict):
        """
        checks if the user requesting a bot action is allowed to do so
        """

        uid_level_list =[]
        for row in range(len(self.config.items("PermissionGroup0"))):
            uid_level_list.append(self.config.items("PermissionGroup0")[row][0])

        if req_dict['invoker']['uid'] in uid_level_list:
            self.user_permission_level = 0
        else:
            uid_level_list = []
            for row in range(len(self.config.items("PermissionGroup1"))):
                uid_level_list.append(self.config.items("PermissionGroup1")[row][0])

            if req_dict['invoker']['uid'] in uid_level_list:
                self.user_permission_level = 1
            else:
                self.user_permission_level = 2

        cmd = req_dict['cmd']['name']
        self.needed_command_permission_level = 2
        for command in self.config.items("CommandPermissionLevel"):
            if cmd == command[0]:
                self.needed_command_permission_level = command[1]

        if self.user_permission_level <= self.needed_command_permission_level:
            return True
        else:
            return False

    def check_command_priority(self, req_dict):

        for row in range(len(self.config.items("RepeatingCommands"))):
            self.repeating_command_list.append(self.config.items("RepeatingCommands")[row][0])

        if req_dict['cmd']['name'] in self.repeating_command_list:
            return False
        else:
            return True


    def queue_parser(self, req_dict):
        print(req_dict)
        if self.check_permission(req_dict) == True:
            if self.check_command_priority(req_dict) == True:
                self.priority_queue.put(req_dict)
            else:
                self.repeating_queue.put(req_dict)
        else:
            req_dict['cmd']['name'] = "msg"
            req_dict['cmd']['args'] = (req_dict['invoker']['clid'],
            "your permission level ({}) is not high enough to use that command!"
            "You need at least permission level {} to use is".
            format(self.user_permission_level, self.needed_command_permission_level))
            

''''

if req_dict['cmd']['repeats'] > 0:
    req_dict['cmd']['repeats'] = req_dict['cmd']['repeats']-1
'''

# {uid: kwmSMgerowmvOG3tod=, cmd: {cmd: pokespam, forced_priority: False, is_on_repeat: True}}