# -*- coding:utf-8 -*-
import os
# python 3.6+
from typing import Union
from enum import Enum

from wechaty import Wechaty, Message, Contact, Room
from wechaty.plugin import WechatyPlugin

from utils.extract_wechat_msg import split_quote_and_mention
from lib.log import LoggerAdaptor
from config import settings

import logging
import subprocess
import argparse

_logger = logging.Logger(__file__)

import time

try:
    from shutil import which
except:
    from distutils.spawn import find_executable as which


class HelpPlugin(WechatyPlugin):

    logger = LoggerAdaptor("HelpPlugin", _logger)

    HELP_HINT = "帮助"
    USAGE = """
        help : 输出帮助指令
        cmd|命令 <CMD> <ARGS>... [--Opt]... : 输入目标机器 Linux 命令 
        rpc : 输入远程调用目标 <仅主人可以使用>
        chat [--model] ： 启动应答机器人 <仅支持私聊>
        wxapi <API_NAME>: 启动微信开发接口功能 <还在开发中...>
        assistant|群聊助手: 开启群聊管理(拉新，踢广告<开启投票，自动处理, 举报>，投票，活跃氛围) <仅主人可以使用>
    
    """

    def __init__(self):
        super(HelpPlugin, self).__init__()

    async def on_message(self, msg : Message):
        self_contact = await self.bot.my_self()
        from_contact = msg.talker()
        txt = msg.text()

        # check whether txt is a xml string
        is_xml_msg = False
        tree = None
        self.bot.msg_type = ""
        try:
            tree = self.bot.parse(txt)
            self.bot.get_msg_type(tree)
            if self.bot.msg_type != "":
                # the bot extract useful xml patterns
                is_xml_msg = True
        except Exception as e:
            pass

        # chatting info
        room = msg.room()

        quoted, text, mention = split_quote_and_mention(txt, tree)
        to_bot = self_contact.get_id() in msg.payload.mention_ids or \
                 self_contact.payload.name == mention or \
                 (is_xml_msg and self.bot.is_pat()) # someone is patting me
        conversation: Union[Room, Contact] = from_contact if room is None else room

        if not (is_xml_msg and self.bot.is_pat()) and self_contact.get_id() != msg.payload.to_id:
            await conversation.ready()
            await self.dispatch(conversation, txt)
            return
        if not to_bot: # the message may not send to any people
            if room is None:
                # maybe an app is pushing message to me
                if from_contact.weixin() == "": # you don't have a valid wechat id, you must be a robot! No way!
                    self.logger.info(f"unverified user msg: {txt}")
                    return

                if is_xml_msg and self.bot.is_app_push():
                    self.logger.info(f"ignore subscription : {txt}")
                    return
            else:
                # no people is talking to or patting me
                self.logger.info(f"no people is talking to me in room : {txt}")
                return
        await conversation.ready()

        # wait for one second
        time.sleep(1)

        if is_xml_msg:
            if self.bot.is_pat():
                await conversation.say(f"{settings.BOT_PROLOG} {self.usage}")
        else:
            await self.dispatch(conversation, txt)


    async def dispatch(self, conversation, txt):
        if txt == "help" or txt == "Help" or txt == "HELP" or txt == "帮助":
            await conversation.say(f"{settings.BOT_PROLOG} {self.usage}")

        if txt.startswith("rpc") or txt.startswith("Rpc") or txt.startswith("RPC"):
            self.bot.state = self.bot.__class__.State.RPC

        if txt.startswith("wxapi") or txt.startswith("Wxapi") or txt.startswith("WXAPI"):
            self.bot.state = self.bot.__class__.State.WXAPI

        if self.bot.state == self.bot.__class__.State.RPC:
            await conversation.say(f"{settings.BOT_PROLOG} rpc is not implemented yet!")

        if self.bot.state == self.bot.__class__.State.WXAPI:
            await conversation.say(f"{settings.BOT_PROLOG} wxapi is not implemented yet!")

    @property
    def usage(self):
        return self.USAGE

    @property
    def name(self):
        return "HelpPlugin"


class LinuxAutomation(WechatyPlugin):

    logger = LoggerAdaptor("LinuxAutomation", _logger)
    TEST_CMD = 'ls -l'
    TEST_CMD = TEST_CMD.split(' ')
    TEST_CMD[0] = which(TEST_CMD[0])

    class State(Enum):
        UNDEF_STATE = -1
        READY = 1
        WAITING = 2
        EXECUTING = 3
        CHECKING = 4
        DONE = 5

    def __init__(self):
        super(LinuxAutomation, self).__init__()
        self.state = LinuxAutomation.State.UNDEF_STATE
        # dialog management
        self.cur_visior_id = None
        self.hold_conversation_from_id = None
        self.hold_conversation_cmd_req = None
        pass

    async def on_message(self, msg : Message):
        self_contact = await self.bot.my_self()
        from_contact = msg.talker()
        txt = msg.text()

        # check whether txt is a xml string
        is_xml_msg = False
        tree = None
        self.bot.msg_type = ""
        try:
            tree = self.bot.parse(txt)
            self.bot.get_msg_type(tree)
            if self.bot.msg_type != "":
                # the bot extract useful xml patterns
                is_xml_msg = True
        except Exception as e:
            pass

        if is_xml_msg:
            # this plugin does not deal with xml string
            return

        # chatting info
        room = msg.room()

        if self_contact.get_id() != msg.payload.from_id:
            # await msg.say(f"{settings.BOT_PROLOG} you are not the master, refuse to go ahead!")
            return

        quoted, text, mention = split_quote_and_mention(txt)
        to_bot = self_contact.get_id() in msg.payload.mention_ids or \
                 self_contact.payload.name == mention
        conversation : Union[Room, Contact] = from_contact if room is None else room
        self.cur_visior_id = from_contact.get_id()

        if self_contact.get_id() != msg.payload.to_id:
            await conversation.ready()
            await self.dispatch(conversation, txt)
            return
        if not to_bot:
            # do nothing to allow capture cmd message actively
            pass
        await conversation.ready()

        # wait for one second
        time.sleep(1)

        await self.dispatch(conversation, txt)

    async def dispatch(self, conversation, txt):
        if txt.startswith("cmd") or txt.startswith("Cmd") or txt.startswith("CMD") or txt.startswith("命令"):
            self.bot.state = self.bot.__class__.State.CMD

            if self.state == LinuxAutomation.State.UNDEF_STATE or \
               self.state == LinuxAutomation.State.DONE:
                # start a new command session
                self.state = LinuxAutomation.State.READY
                self.hold_conversation_from_id = self.cur_visior_id # == self_contact.get_id()

        if self.state == LinuxAutomation.State.READY \
                and self.hold_conversation_from_id is not None \
                and self.hold_conversation_from_id == self.cur_visior_id:
            command = await self.comprehend(txt)
            if command is None:
                await conversation.say(f"{settings.BOT_PROLOG} {txt} cannot be parsed into a valid and safe cmd for use!")
                return
            if len(command) == 0:
                self.state = LinuxAutomation.State.WAITING
                await conversation.say(f"{settings.BOT_PROLOG} please input linux cmd ...")
                return
            else:
                command[0] = which(command[0])
                command_str = "".join(command)
                self.state = LinuxAutomation.State.CHECKING
                self.hold_conversation_cmd_req = command
                await conversation.say(f"{settings.BOT_PROLOG} executing <{command_str}> ?")
                return

        if self.state == LinuxAutomation.State.WAITING \
                and self.hold_conversation_from_id is not None \
                and self.hold_conversation_from_id == self.cur_visior_id:
            raw_command_args = txt.split(' ')
            # Note: for safety we will only run user command when it is deployed inside a docker container
            command = raw_command_args
            command[0] = which(command[0])
            command_str = "".join(command)
            self.state = LinuxAutomation.State.CHECKING
            self.hold_conversation_cmd_req = command
            await conversation.say(f"{settings.BOT_PROLOG} executing <{command_str}> ?")
            return

        if self.state == LinuxAutomation.State.CHECKING \
                and self.hold_conversation_from_id is not None \
                and self.hold_conversation_from_id == self.cur_visior_id:
            if txt == "y" or txt == "Y" or txt == "yes" or txt == "Yes" or txt == "YES" or txt == "是":
                # Note: for safety we will only run user command when it is deployed inside a docker container
                ret = await self.run_a_cmd(self.TEST_CMD)
                await conversation.say(f"{settings.BOT_PROLOG} {ret}")
                await conversation.say(f"{settings.BOT_PROLOG} executing <CMD : {self.hold_conversation_cmd_req}> completes")
                self.state = LinuxAutomation.State.DONE
            else:
                self.state = LinuxAutomation.State.DONE


    async def run_a_cmd(self, cmd_args, **kwargs):
        return subprocess.check_output(cmd_args).decode("utf-8")


    async def comprehend(self, txt):
        # @todo TODO passing with argparse
        import re
        cmd_regex = re.compile(r"""
        (cmd|Cmd|CMD|命令)\s*\:?\s* 
        (?P<cmd>.*)
        """, re.VERBOSE)
        searched = cmd_regex.search(txt)
        if searched is not None:
            if searched.groupdict().get('cmd', None) is not None \
                    and searched.groupdict()['cmd'] != "":
                raw_command_args = searched.groupdict()['cmd'].split(' ')
                parser = argparse.ArgumentParser(description=__doc__, usage='')
                parser.add_argument('argv', nargs=argparse.REMAINDER, help="arguments for user command")

                args = parser.parse_args(raw_command_args)

                return args.argv
            else:
                return []
        else:
            return None

    @property
    def name(self):
        return "LinuxAutomation"


class TaskMgrPlugin(WechatyPlugin):

    def __init__(self):
        super(TaskMgrPlugin, self).__init__()

        self.plugins = [LinuxAutomation(), HelpPlugin()]

    async def on_message(self, msg: Message):
        # clear chatting status
        self.bot.msg_type = ""


    async def init_plugin(self, wechaty : Wechaty):
        # set bot for this plugin
        self.bot = wechaty
        self.bot.use(self.plugins)

        # set bot for all other plugins
        for plugin in self.plugins:
            plugin.set_bot(self.bot)
            await plugin.init_plugin(self.bot)

    @property
    def name(self):
        return "TaskMgrPlugin"