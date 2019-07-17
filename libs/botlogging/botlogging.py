#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________
from PYRobot.libs.botlogging.coloramadefs import *


level_DEBUG = 40
level_INFO = 30
level_WARNING = 20
level_ERROR = 10
level_CRITICAL = 0

class Logging(object):
    def __init__(self,level=50):
        self._etc["Logging_level"]=level

    def Level_reconfigure(self,level=50):
        self._etc["Logging_level"]=level

    def L_debug(self, men):
        if self._etc["Logging_level"] >= level_WARNING:
            print(log_color("[[FG]Debug[SR]] <"+self._etc["name"]+">::"+str(men)))

    def L_warning(self, men):
        if self._etc["Logging_level"] >= level_WARNING:
            print(log_color("[[FY]Warning[SR]] <"+self._etc["name"]+">::"+str(men)))

    def L_info(self, men):
        if self._etc["Logging_level"] >= level_INFO:
            print(log_color("[[FC]Info[SR]] <"+self._etc["name"]+">::"+str(men)))

    def L_error(self, men):
        if self._etc["Logging_level"] >= level_INFO:
            print(log_color("[[FR]ERROR[SR]] <"+self._etc["name"]+">::"+str(men)))

    def L_critical(self, men):
        if self._etc["Logging_level"] >= level_INFO:
            print(log_color("[[FR]CRITICAL[SR]]:<"+self._etc["name"]+"> "+str(men)))

    def L_print(self, men,handler=False):
        if handler:
            print(log_color("[FG]<"+self._etc["name"]+"> [SR]"+str(men)))
        else:
            print(log_color(str(men)))
