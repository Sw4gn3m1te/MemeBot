import ts3
from threading import Thread
import logging
import configparser
from random import randint
import commands


logging.basicConfig(filename="log.log", level=logging.INFO)

def exception_logger(function):

    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(function.__name__)
            logger.error(e, *args, **kwargs)

    return wrapper

class Bot:
    """
    Teamspeak 3 Bot
    """

    @exception_logger
    def __init__(self, host, port, serverid, username, password, defaultchannelid, botname):
        """
        creates Bot
        :param host: address the bot connects to
        :param port: port on which the bot connects to the server (10011 is the standard port)
        :param sid: server ID which the bot connects to (1 if only one server is running on the server)
        :param username: username to login as a server query
        :param password: password to login as a server query
        :param defaultchannel: the channel the bot connects to after joining the server
        :param botname: the name of the bot
        """

        self.event = None
        self.c = None

        self.host = host
        self.port = port
        self.sid = serverid
        self.username = username
        self.password = password
        self.default_channel_id = defaultchannelid
        self.bot_name = botname

        self.kill_keep_alive = False

        self.connect()
        self.setup_bot()
        self.start_keep_alive_loop()

    @exception_logger
    def connect(self):
        """
        connects the bot to the server
        """

        self.c = ts3.query.TS3Connection(self.host, self.port)

    @exception_logger
    def disconnect(self):
        """
        closes connection to server and shuts down keeps alive thread
        """
        self.kill_keep_alive = True
        while True:
            if self.t_keep_alive.is_alive():
                continue

            self.c.close()

    @exception_logger
    def setup_bot(self):
        """
        selects server, sets nickname, joins defaultchannel, stats the eventhandler
        """

        self.c.login(client_login_name=self.username, client_login_password=self.password)
        self.c.use(sid=self.sid)
        self.c.clientupdate(client_nickname=self.bot_name)
        self.c.clientmove(clid=self.c.whoami()[0]["client_id"], cid=self.default_channel_id)

        self.c.servernotifyregister(event="textserver")  # targetmode 3
        self.c.servernotifyregister(event="textchannel")  # targetmode 2
        self.c.servernotifyregister(event="textprivate")  # targetmode 1

    @staticmethod
    @exception_logger
    def create_ts3_viewer_bot(host, sid, server_port=9987, query_port=10011):
        c = ts3.query.TS3Connection(host, query_port)
        c.use(sid=sid, port=server_port)

    @staticmethod
    @exception_logger
    def create_bot_from_config():
        """
        loads bot settings from config.ini file
        """

        '''
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.host = config.items("General")[0][1]
        self.port = config.items("General")[1][1]
        self.sid = config.items("General")[2][1]
        self.username = config.items("General")[3][1]
        self.password = config.items("General")[4][1]
        self.bot_name = config.items("General")[5][1]
        self.default_channel_id = config.items("General")[6][1]
        '''

        config = configparser.ConfigParser(allow_no_value=True)
        config.read("config.ini")
        settings = config.items('General')
        settings = dict(settings)
        return Bot(**settings)

    @exception_logger
    def start_keep_alive_loop(self):
        """
        sends a keep alive signals to the server and starts waiting for events
        """
        global event
        def keep_alive_loop(interval=5):

            while True:
                if self.kill_keep_alive == True:
                    break
                self.c.send_keepalive()
                try:
                    event = self.c.wait_for_event(interval)
                    commands.CommandHandler(self.c, event)
                except:
                    pass



        self.t_keep_alive = Thread(target=keep_alive_loop)
        self.t_keep_alive.start()


b = Bot.create_bot_from_config()

'''
einer dc'ed nicht NANI?

b2 = Bot.create_bot_from_config()
b = Bot.create_non_config_bot("192.168.0.4", 10011, 1, "serveradmin", "6xxhEjoC", 8, "werwrew")
b.disconnect()
b2.disconnect()
'''
