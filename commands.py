import json
import queue
import logging
import bot


class CommandHandler:
    """
    handles the permissions as well as the order of the command execution
    """
    def __init__(self, event):

        self.event = event
        self.req_dict = {}

        self.repeating_command_list = []
        self.user_permission_level = 0
        self.needed_command_permission_level = 3

        with open('config.json', 'r') as f:
            self.config = json.load(f)

        #self.req_dict = self.parse_msg_to_req_dict()
        #self.queue_filler(self.req_dict)



        """
        if type event = req_dict then....
        other __init__
        """

    def check_for_command_character(self):
        cc = self.config['CommandCharacter']
        self.command_character = cc[0][0]

        msg = str(self.event[0]['msg'])
        if msg[:len(self.command_character)] == self.command_character:
            return True
        else:
            return False


    def parse_msg_to_req_dict(self):
        # {'targetmode': '3', 'msg': '#test', 'invokerid': '2', 'invokername': 'DRAW MONSTA CARDO', 'invokeruid': 'VUIuVaoZpicscTxXuM6kO+7j1hM='}
        msg = str(self.event[0]['msg'])

        invoker_name = str(self.event[0]['invokername'])
        invoker_uid = str(self.event[0]['invokeruid'])
        invoker_clid = str(self.event[0]['invokerid'])

        #except Index error
        msg = msg[len(self.command_character):]
        arglist = msg.split()
        cmd_name = arglist[0].lower()
        cmd_args = arglist[1:]

        repeats = 0
        if cmd_name in self.config['RepeatingCommands'].keys():
            repeats = cmd_args[1] #2 arg aus cmd args

        req_dict = {"invoker": {"name": invoker_name, "uid": invoker_uid, "clid": invoker_clid},
                    "cmd": {"name": cmd_name, "args": cmd_args, "repeats": repeats}}

        self.req_dict = req_dict
        return req_dict

    def check_permission(self):
        """
        checks if the user requesting a bot action is allowed to do so
        """
        print(self.req_dict)
        if self.req_dict['invoker']['uid'] in self.config['PermissionGroup3'].keys():
            self.user_permission_level = 3
        elif self.req_dict['invoker']['uid'] in self.config['PermissionGroup2'].keys():
                self.user_permission_level = 2
        else:
                self.user_permission_level = 1

        req_cmd = self.req_dict['cmd']['name']
        self.needed_command_permission_level = 3

        for cmd_in_file in self.config['CommandPermissionLevel'].items():
            if req_cmd == cmd_in_file[0]:
                self.needed_command_permission_level = cmd_in_file[1]
                break

        if self.user_permission_level >= self.needed_command_permission_level:
            return True, self.user_permission_level, self.needed_command_permission_level
        else:
            return False, self.user_permission_level, self.needed_command_permission_level

    def check_priority(self):
        if self.req_dict['cmd']['name'] in self.config['RepeatingCommands'].keys():
            return False
        else:
            return True


class CommandExecute:

    def __init__(self, c, req_dict):

        self.c = c
        self.req_dict = req_dict
        self.choose_command()

    def choose_command(self):

        cmd = self.req_dict['cmd']['name']
        if cmd == 'help':
            self.help()

        elif cmd == 'b':
            self.b(*self.req_dict['cmd']['args'])

        elif cmd == 'data':
            self.data()

    def help(self):
        print("yeet")

    def data(self):
        resp = self.c.clientlist()
        for client in resp:
            if client["client_type"] == "1":
                pass
            else:
                id = client["clid"]
                name = client["client_nickname"]
                self.c.sendtextmessage(targetmode=1, target=self.req_dict['invoker']['clid'], msg=str(name + ":  " + id))

    def b(self, clid, duration, reason):

        self.c.sendtextmessage(targetmode=1, target=clid, msg=duration)
        #self.c.sendtextmessage(targetmode=1, target=self.req_dict['invoker']['clid'], msg=clid)
        """
        Usage: b <clid> <duration> <reason>
        """
    def pokespam(self, target, ammount, msg):
        self.c.clientpoke(target, msg)
        if self.req_dict['cmd']['repeats'] > 0:
            self.req_dict['cmd']['repeats'] = self.req_dict['cmd']['repeats'] - 1





'''

if req_dict['cmd']['repeats'] > 0:
    req_dict['cmd']['repeats'] = req_dict['cmd']['repeats']-1


# {uid: kwmSMgerowmvOG3tod=, cmd: {cmd: pokespam, forced_priority: False, is_on_repeat: True}}

    def command(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__name__)
                logger.error(e)
                cmd = self.req_dict['cmd']['name']
                self.req_dict['cmd']['name'] = "msg"
                if e == TypeError:
                    self.req_dict['cmd']['args'] = [self.req_dict['invoker']['clid'], "Wrong command usage.\n"
                                                                                      "{}".format(cmd.__doc__)]
                else:
                    self.req_dict['cmd']['args'] = [self.req_dict['invoker']['clid'], "Error during command execution"]

                print(self.req_dict)
                return CommandExecute(self.c, self.req_dict)

        return wrapper

'''