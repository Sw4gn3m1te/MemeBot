import ts3
import logging
import json
import commands
import queue
import cmd_queue
from time import sleep

logging.basicConfig(filename="./log.log", level=logging.INFO)


def exception_logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__name__)
            logger.error(e)
    return wrapper


class Bot:
    """
    Teamspeak 3 Bot
    """
    @exception_logger
    def __init__(self, host, queryport, serverport, serverid, username, password, defaultchannelid, botname):
        """
        creates Bot
        :param host: address the bot connects to
        :param port: port on which the bot connects to the server (10011 is the standard port)
        :param serverid: server ID which the bot connects to (1 if only one server is running on the server)
        :param username: username to login as a server query
        :param password: password to login as a server query
        :param defaultchannelid: the channel the bot connects to after joining the server
        :param botname: the name of the bot
        """

        self.event = None
        self.kill_keep_alive = False

        self.host = host
        self.query_port = queryport
        self.server_port = serverport
        self.sid = serverid
        self.username = username
        self.password = password
        self.default_channel_id = defaultchannelid
        self.bot_name = botname

        self.c = self.connect()
        self.setup_bot()

        print("Bot started!")

    @exception_logger
    def connect(self):
        """
        connects the bot to the server
        """
        self.c = ts3.query.TS3ServerConnection(self.host, self.query_port)
        return self.c

    @exception_logger
    def disconnect(self):
        """
        closes connection to server and shuts down keeps alive thread
        """
        self.kill_keep_alive = True
        sleep(1)
        self.c.close()

    @exception_logger
    def setup_bot(self):
        """
        selects server, sets nickname, joins defaultchannel, starts the eventhandler
        """

        self.c.exec_("login", client_login_name=self.username, client_login_password=self.password)
        self.c.exec_("use", sid=self.sid, port=self.server_port)
        self.c.exec_("clientupdate", client_nickname=self.bot_name)
        self.c.exec_("clientmove", clid=self.c.query("whoami").all()[0]["client_id"], cid=self.default_channel_id)

        self.c.exec_("servernotifyregister", event="textserver")
        self.c.exec_("servernotifyregister", event="textchannel")
        self.c.exec_("servernotifyregister", event="textprivate")


    @staticmethod
    @exception_logger
    def create_ts3_viewer_bot(host, sid, server_port=9987, query_port=10011):
        c = ts3.query.TS3ServerConnection(host, query_port)
        c.query("use", sid=sid, port=server_port)

    @staticmethod
    @exception_logger
    def create_bot_from_config():
        """
        loads bot settings from config.ini file
        """

        """ 
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.host = config.items("General")[0][1]
        self.port = config.items("General")[1][1]
        self.sid = config.items("General")[2][1]
        self.username = config.items("General")[3][1]
        self.password = config.items("General")[4][1]
        self.bot_name = config.items("General")[5][1]
        self.default_channel_id = config.items("General")[6][1]
        """

        with open('config.json', 'r') as f:
            config = json.load(f)

        return Bot(**config['Default'])

    @exception_logger
    def keep_alive_loop(self, interval=0.1):
        while not self.kill_keep_alive:
            self.c.send_keepalive()
            try:
                self.event = self.c.wait_for_event(interval)
            except TimeoutError:
                return None
                pass
            else:
                return self.event


if __name__ == '__main__':
    b = Bot.create_bot_from_config()
