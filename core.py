import bot, commands, cmd_queue, json, logging

if __name__ == '__main__':

        logging.basicConfig(filename="./log.log", level=logging.INFO)
        global req_dict
        logger = logging.getLogger('core')
        cmd_queue = cmd_queue.CommandQueue()
        b = bot.Bot.create_bot_from_config()

        while True:

            try:

                event = b.keep_alive_loop()

                if event is not None:
                    ch = commands.CommandHandler(event)
                    if ch.check_for_command_character():
                        req_dict = ch.parse_msg_to_req_dict()

                        permission = ch.check_permission()
                        allowed_bool = permission[0]
                        current_permission_level = permission[1]
                        needed_permission = permission[2]

                        req_dict['cmd']['permission']['have'] = current_permission_level
                        req_dict['cmd']['permission']['need'] = needed_permission
                        print(req_dict)
                        logger.info(str(req_dict))

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
                    req_dict = cmd_queue.get_next_command()
                    if req_dict is not None:
                        if req_dict['cmd']['name'] == 'stop':
                            cmd_queue.clear_queues()
                            continue
                        try:
                            ce = commands.CommandExecute(b.c, req_dict)
                        except TypeError as e:
                            logger.error(e)
                            cmd_name = req_dict['cmd']['name']
                            req_dict['cmd']['name'] = "msg"
                            req_dict['cmd']['args'] = [req_dict['invoker']['clid'],
                                                       "Wrong usage of command {} use *help {} for correct syntax"
                                                       .format(cmd_name, cmd_name)]
                            cmd_queue.add_to_priority_queue(req_dict)
                            continue
                        except Exception as e:
                            logger.error(e)
                            req_dict['cmd']['name'] = "msg"
                            req_dict['cmd']['args'] = [req_dict['invoker']['clid'], "Error during command execution"]
                            cmd_queue.add_to_priority_queue(req_dict)
                            continue

                        while not ce.command_done:
                            continue
                        else:
                            try:
                                if int(req_dict['cmd']['repeats']) > 1:
                                    req_dict['cmd']['repeats'] = ce.repeats_left
                                    cmd_queue.add_to_normal_queue(req_dict)
                            except ValueError:
                                cmd_name = req_dict['cmd']['name']
                                req_dict['cmd']['name'] = "msg"
                                req_dict['cmd']['args'] = [req_dict['invoker']['clid'],
                                                           "Wrong usage of command {} use *help {} for correct syntax".
                                                               format(cmd_name, cmd_name)]

                            else:
                                pass
                    else:
                        pass

            except Exception as unexpected:
                logger.error(unexpected)
                continue
