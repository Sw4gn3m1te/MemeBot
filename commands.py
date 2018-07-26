import json
import queue
import logging
import bot
import asyncio
import rainbowsix
from subprocess import call
import random
import ts3


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


    def check_for_command_character(self):
        cc = self.config['CommandCharacter']
        self.command_character = cc[0][0]

        msg = str(self.event[0]['msg'])
        if msg[:len(self.command_character)] == self.command_character:
            return True
        else:
            return False


    def parse_msg_to_req_dict(self):

        msg = str(self.event[0]['msg'])
        try:
            invoker_name = str(self.event[0]['invokername'])
            invoker_uid = str(self.event[0]['invokeruid'])
            invoker_clid = str(self.event[0]['invokerid'])
        except KeyError:
            print(self.event[0])

        #except Index error
        msg = msg[len(self.command_character):]
        arglist = msg.split()
        cmd_name = arglist[0].lower()
        cmd_args = arglist[1:]

        repeats = 0
        if cmd_name in self.config['RepeatingCommands'].keys():
            repeats = cmd_args[-1] #letzte arg aus cmd args
            cmd_args = cmd_args[:-1]

        req_dict = {"invoker": {"name": invoker_name, "uid": invoker_uid, "clid": invoker_clid},
                    "cmd": {"name": cmd_name, "args": cmd_args, 'repeats': repeats}}

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
        self.repeats_left = 0
        self.command_done = False
        self.choose_command()


    def choose_command(self):

        cmd = self.req_dict['cmd']['name']

        if cmd == 'help':
            self.help(*self.req_dict['cmd']['args'])

        elif cmd == 'data':
            self.data()

        elif cmd == 'b':
            self.b(*self.req_dict['cmd']['args'])

        elif cmd == 'database':
            self.database()

        elif cmd == 'pokespam':
            self.pokespam(*self.req_dict['cmd']['args'])

        elif cmd == 'r6rank':
            self.r6rank(*self.req_dict['cmd']['args'])

        elif cmd == 'r6ops':
            self.r6ops(*self.req_dict['cmd']['args'])

        elif cmd == 'trollmove':
            self.trollmove(*self.req_dict['cmd']['args'])

        elif cmd == 'botrename':
            self.botrename(*self.req_dict['cmd']['args'])

    def help(self, command=None): #execpt type error
        """
        Usage: help <command>
        """
        if command is None:
            self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg="There is no help ;)")
        else:
            self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                         msg="help text for {}".format(command))
        self.command_done = True

    def botrename(self, name):
        self.c.exec_("clientupdate", client_nickname=name)

    def data(self):
        """
        Usage: data <clientid>
        """

        resp = self.c.exec_("clientlist")

        for client in resp:
            if client["client_type"] == "1":
                pass
            else:
                id = client["clid"]
                name = client["client_nickname"]
                self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                             msg=str(name + ":  " + id))
        self.command_done = True

    def database(self):
        """
        Usage: database
        """
        for line in self.c.exec_("clientdblist"):
            self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg=line)
        self.command_done = True

    def b(self, clid, duration, reason):

        """
        Usage: b <clid> <duration> <reason>
        """

        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                     msg="{} has been banned".format(clid))
        self.c.exec_("banclient", clid=clid, time=duration, banreason=reason)
        self.command_done = True

    def r6ops(self, playername, operator):
        r = rainbowsix.RainbowSix()
        asyncio.get_event_loop().run_until_complete(r.server_auth("some mail", "some pw")) #
        asyncio.get_event_loop().run_until_complete(r.get_op_stats(playername, operator))
        r.draw_op()
        call(split("sudo cp ./op_stat_img.png /var/www/html"))
        self.c.exec_("channeledit", cid=37, channel_description="[img]some url/op_stat_img.png?{}[/img]".format(str(random.randint(1, 1E20)))) #
        self.command_done = True

    def r6rank(self, playername):
        r = rainbowsix.RainbowSix()
        asyncio.get_event_loop().run_until_complete(r.server_auth("some mail", "some pw")) #
        asyncio.get_event_loop().run_until_complete(r.get_ranked_stats(playername))
        r.draw_ranked()
        call(split("sudo cp ./op_stat_img.png /var/www/html"))
        self.c.exec_("channeledit", cid=37, channel_description="[img]tnl5.ddns.net/op_stat_img.png?{}[/img]".format(str(random.randint(1, 1E20))))
        self.command_done = True
        self.command_done = True

    def pokespam(self, target, msg):
        repeats = self.req_dict['cmd']['repeats']
        self.c.exec_("clientpoke", clid=target, msg=msg)
        if int(repeats) > 0:
            self.repeats_left = int(repeats) - 1
        else:
            self.repeats_left = 0
        self.command_done = True

    def trollmove(self, target):
        repeats = self.req_dict['cmd']['repeats']
        channels = self.c.exec_("channellist")
        cid_list = [channel["cid"] for channel in channels]
        try:
            self.c.exec_("clientmove", clid=target, cid=random.choice(cid_list))
        except ts3.query.TS3QueryError:
            pass
        if int(repeats) > 0:
            self.repeats_left = int(repeats) - 1
        else:
            self.repeats_left = 0
        self.command_done = True




'''
def command(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__name__)
            logger.error(e)


            req_dict['cmd']['name'] = "msg"
            if e == TypeError:
                self.req_dict['cmd']['args'] = [self.req_dict['invoker']['clid'], "Wrong command usage.\n"
                                                                                  "{}".format(cmd.__doc__)]
            else:
                self.req_dict['cmd']['args'] = [self.req_dict['invoker']['clid'], "Error during command execution"]

            print(self.req_dict)
            return CommandExecute(self.c, self.req_dict)



    return wrapper
'''
