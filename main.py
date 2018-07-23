import bot, commands, cmd_queue, json


cmd_queue = cmd_queue.CommandQueue()
b = bot.Bot.create_bot_from_config()


while True:

    event = b.keep_alive_loop()

    if event is not None:
        ch = commands.CommandHandler(event)
        if ch.check_for_command_character():
            req_dict = ch.parse_msg_to_req_dict()

            permission = ch.check_permission()
            allowed_bool = permission[0]
            current_permission_level = permission[1]
            needed_permission = permission[2]
            print(permission)

            if allowed_bool:
                if ch.check_priority():
                    cmd_queue.add_to_priority_queue(req_dict)
                else:
                    cmd_queue.add_to_normal_queue(req_dict)
            else:
                req_dict['cmd']['name'] = "msg"
                req_dict['cmd']['args'] = (req_dict['invoker']['clid'],
                                           "your permission level ({}) is not high enough to use that command!"
                                           "You need at least permission level {} to use it".
                                           format(current_permission_level, needed_permission))
                cmd_queue.add_to_priority_queue(req_dict)

    else:
        command = cmd_queue.get_next_command()
        if command is not None:
            commands.CommandExecute(b.c, command)
        else:
            pass


