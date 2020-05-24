import json
import queue
import logging
import bot
import asyncio
import rainbowsix
from subprocess import check_output
from subprocess import call
import random
import ts3
from shlex import split
from datetime import datetime

logging.basicConfig(filename="./log.log", level=logging.INFO)


def exception_logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__name__)
            logger.error(e)
    return wrapper


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

    @exception_logger
    def check_for_command_character(self):
        cc = self.config['CommandCharacter']
        self.command_character = cc[0][0]

        msg = str(self.event[0]['msg'])
        if msg[:len(self.command_character)] == self.command_character:
            return True
        else:
            return False

    @exception_logger
    def parse_msg_to_req_dict(self):

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
            if not len(cmd_args) == 0:
                repeats = cmd_args[-1]
                cmd_args = cmd_args[:-1]

        req_dict = {"invoker": {"name": invoker_name, "uid": invoker_uid, "clid": invoker_clid},
                    "cmd": {"name": cmd_name, "args": cmd_args, 'repeats': repeats,
                            "permission": {"have": "", "need": ""}}}

        self.req_dict = req_dict
        return req_dict

    @exception_logger
    def check_permission(self):
        """
        checks if the user requesting a bot action is allowed to do so
        """
        if self.req_dict['invoker']['uid'] in self.config['PermissionGroup4'].keys():
            self.user_permission_level = 4
        elif self.req_dict['invoker']['uid'] in self.config['PermissionGroup3'].keys():
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

    @exception_logger
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
        self.ft = ts3.filetransfer.TS3FileTransfer(self.c)
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.choose_command()

    def choose_command(self):

        cmd = self.req_dict['cmd']['name']

        if cmd == 'help':
            self.help(*self.req_dict['cmd']['args'])

        elif cmd == 'msg':
            self.msg(*self.req_dict['cmd']['args'])

        elif cmd == 'data':
            self.data()

        elif cmd == 'b':
            self.b(*self.req_dict['cmd']['args'])

        elif cmd == 'database':
            self.database()

        elif cmd == 'pokespam' or 'pokespamf':
            self.pokespam(*self.req_dict['cmd']['args'])

        elif cmd == 'r6rank':
            self.r6rank(*self.req_dict['cmd']['args'])

        elif cmd == 'r6ops':
            self.r6ops(*self.req_dict['cmd']['args'])

        elif cmd == 'trollmove' or 'trollmovef':
            self.trollmove(*self.req_dict['cmd']['args'])

        elif cmd == 'botrename':
            self.botrename(*self.req_dict['cmd']['args'])

        elif cmd == 'block':
            self.block(*self.req_dict['cmd']['args'])

        elif cmd == 'unblock':
            self.unblock(*self.req_dict['cmd']['args'])

        elif cmd == 'resetiptables':
            self.resetiptables()

        elif cmd == 'blocklist':
            self.blocklist()

        elif cmd == 'lastseen':
            self.lastseen(*self.req_dict['cmd']['args'])

        elif cmd == 'dc':
            self.c.close()

        else:
            self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                         msg="command {} not found".format(cmd))
            self.command_done = True

    def help(self, command=None):

        if command is None:
            for key in self.config['HelpText'].keys():
                if self.req_dict['cmd']['permission']['have'] >= self.config['CommandPermissionLevel'][key]:
                    msg = key + ": " + self.config['HelpText'][key]
                    self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                                 msg=msg)
        else:
            if self.req_dict['cmd']['permission']['have'] >= self.config['CommandPermissionLevel'][command]:
                msg = command + ": " + self.config['HelpText'][command]
                self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                             msg=msg)
            else:
                self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                             msg="command {} not found".format(command))

        self.command_done = True

    def msg(self, target, msg):
        self.c.exec_("sendtextmessage", targetmode=1, target=target,
                     msg=msg)
        self.command_done = True

    def botrename(self, name):
        self.c.exec_("clientupdate", client_nickname=name)
        self.command_done = True

    def data(self):

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

        for line in self.c.exec_("clientdblist"):
            self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg=line)
        self.command_done = True

    def b(self, clid, duration, reason):

        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                     msg="{} has been banned".format(clid))
        self.c.exec_("banclient", clid=clid, time=duration, banreason=reason)
        self.command_done = True

    def r6ops(self, playername, operator):
        r = rainbowsix.RainbowSix()
        asyncio.get_event_loop().run_until_complete(r.server_auth(self.config['BotMail'], self.config['BotPw']))
        asyncio.get_event_loop().run_until_complete(r.get_op_stats(playername, operator))
        r.draw_op()
        with open("op_stat_img.png", "rb") as stat_file:
            self.ft.init_upload(input_file=stat_file, name="/op_stat_img.png", cid=2)
        self.c.exec_("channeledit", cid=2, channel_description="[IMG]ts3image://op_stat_img.png?channel=2&path=/[/IMG]")
        self.command_done = True

    def r6rank(self, playername):
        r = rainbowsix.RainbowSix()
        asyncio.get_event_loop().run_until_complete(r.server_auth(self.config['BotMail'], self.config['BotPw']))
        asyncio.get_event_loop().run_until_complete(r.get_ranked_stats(playername))
        r.draw_ranked()
        with open("op_stat_img.png", "rb") as stat_file:
            self.ft.init_upload(input_file=stat_file, name="/op_stat_img.png", cid=2)
        self.c.exec_("channeledit", cid=2, channel_description="[IMG]ts3image://op_stat_img.png?channel=2&path=/[/IMG]")
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

    def block(self, ip, mode):

        if mode == "in":
            call(split("sudo iptables -A INPUT -s {} -j DROP".format(ip)))
        elif mode == "out":
            call(split("sudo iptables -A OUTPUT -d* {} -j DROP".format(ip)))
        elif mode == "full":
            call(split("sudo iptables -A INPUT -s {} -j DROP".format(ip)))
            call(split("sudo iptables -A OUTPUT -d {} -j DROP".format(ip)))
        else:
            self.c.exec_("sendtextmassage", targetmode=1, target=self.req_dict['invoker']['clid'],
                         msg="no changes made! wrong mode specified only (in, out, full) is allowed")
            self.command_done = True
            return

        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                     msg=str("rule for {} ({}) added".format(ip, mode)))
        self.command_done = True

    def unblock(self, ip):
        call(split("sudo iptables -D INPUT -s {} -j DROP".format(ip)))
        call(split("sudo iptables -D OUTPUT -d {} -j DROP".format(ip)))
        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                     msg=str("rules for {} removed".format(ip)))

        self.command_done = True
        return

    def resetiptables(self):
        call(split("sudo iptables -F"))
        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'],
                     msg=str("all rules removed"))
        self.command_done = True

    def blocklist(self):

        result = check_output(split("sudo iptables -L INPUT")).decode("ascii")
        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg=result)
        result = check_output(split("sudo iptables -L OUTPUT")).decode("ascii")
        self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg=result)

        self.command_done = True

    def lastseen(self, cldbid):

        for line in self.c.exec_("clientdblist"):
            if line['cldbid'] == cldbid:
                date = str(datetime.fromtimestamp(int(line['client_lastconnected'])))
                name = line['client_nickname']
                msg = name + "was last seen on: " + date
                self.c.exec_("sendtextmessage", targetmode=1, target=self.req_dict['invoker']['clid'], msg=msg)
            else:
                pass
        self.command_done = True



