#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
import sys
import os
import time
import copy
from PYRobot.libs.server import Run_Server,Start_Server
from PYRobot.libs.proxy import Proxy
import PYRobot.libs.config_comp as conf
import PYRobot.libs.utils as utils
import PYRobot.libs.utils_mqtt as utils_mqtt
import PYRobot.libs.utils_BB as BB
from PYRobot.libs.botlogging.coloramadefs import P_Log
import PYRobot.libs.parser as parser


robots_dir=utils.get_PYRobots_dir()
dir_comp="components/"

def locate_BB(port=9999):
    P_Log("[FY]Finding BigBrother on ethernet segment")
    uri_BB=BB.Get_BigBrother(port)
    if uri_BB!="0.0.0.0:0":
        P_Log("[FY]Located on {}".format(uri_BB))
    return uri_BB

def find_MQTT(mosquito_uri):

    if utils.mqtt_alive(mosquito_uri):
        P_Log("[FY] BROKER MQTT Located on {} [[FG]OK[FY]]".format(mosquito_uri))
    else:
        P_Log("[FY] BROKER MQTT local NOT Located [[FY]ERROR[FW]]")
        mosquito_uri="0.0.0.0:0"
    return mosquito_uri

def Get_BigBrother_proxy(broadcast_port=9999):
    #P_Log("[FY] Finding BigBrother on ethernet segment")
    uri_BB=BB.Get_BigBrother(broadcast_port)
    if uri_BB=="0.0.0.0:0":
        #P_Log("[FR] [warning][FW] BigBrother not found")
        return "0.0.0.0:0",None
    else:
        proxy=Proxy(uri_BB)
        if proxy():
            return uri_BB,proxy
    return uri_BB,None

def Get_BigBrother_config(proxy,robot):
    if proxy is not None:
        default=proxy.Get_Robot(robot)
    else:
        P_Log("[FR] [ERROR][FW] Comunicating with BIGBROTHER")
        exit()
    return default

def Set_BigBrother_config(proxy,robot,conf):
    if proxy is not None:
        proxy.Register_Robot_Conf(robot,conf)
    else:
        P_Log("[FR] [ERROR][FW] Comunicating with BIGBROTHER")
        exit()

def Get_BigBrother_comp(proxy,robot,comp):
    if proxy is not None:
        mycomp=proxy.Get_Comp(comp)
    else:
        P_Log("[FR] [ERROR][FW] Comunicating with BIGBROTHER")
        exit()
    return mycomp

def Get_General(robot_dir):
    dir_etc=robots_dir+robot_dir+"/etc/"
    general=conf.get_conf(dir_etc+"general.json")
    return general

def Get_Instance(robot_dir,component):
    dir_etc=robots_dir+robot_dir+"/etc/"
    instances=conf.get_conf(dir_etc+"instances.json")
    try:
        return instances[component]
    except:
        P_Log("[FR] [ERROR][FW] {} Not found in {}/instances".format(component,robot_dir))
        exit()

class Comp_Starter(object):
    def __init__(self,robot_dir,component,general={},instance={}):
        self.robot_dir=robot_dir
        self.component=component
        dir_etc=robots_dir+robot_dir+"/etc/"
        if general=={}:
            general=Get_General(robot_dir)
        self.general=general
        if instance=={}:
            instance=Get_Instance(robot_dir,component)
        self.instance,errors=parser.instance_check(instance)
        if len(errors)==0:
            P_Log("[FY] component syntactic checking [FG] [OK]")
        else:
            for err in errors:
                P_Log("[FR] [ERROR][FY] Syntactic  in {}-->{}".format(err[0],err[1]))
            exit()
        broadcast_port=general["broadcast_port"]
        self.uri_BB,self.BB=Get_BigBrother_proxy()

    def Get_BB_Robot(self):
        if self.BB():
            general=self.BB.Get_Robot(self.robot)
            if general!={}:
                P_Log("[FY] Robot [FG]{} is online[FY] getting conf".format(self.robot))
                self.general=general
        else:
            P_Log("[FR] [ERROR][FY] Bigbrother not found")
            exit()

    def Get_BB_Comp(self,component):
        if self.BB():
            comp=self.BB.Get_Comp(component)
            if comp!={}:
                P_Log("[FR] [ERROR][FY] {} is online on host:{}".format(component,comp["host"]))
                exit()
        else:
            P_Log("[FR] [ERROR][FY] Bigbrother not found")
            exit()

    def Get_MQTT(self):
        MQTT="{}:{}".format(self.component["_etc"]["ip"],
                self.component["_etc"]["MQTT_port"])
        MQTT_uri=find_MQTT(MQTT)
        if MQTT_uri!="0.0.0.0:0":
            self.component["_etc"]["MQTT_uri"]=MQTT_uri
        else:
            P_Log("[ERROR] Broker {} not available".format(MQTT))
            exit()

    def Create(self,robot=""):
        if robot=="":
            robot=self.robot_dir
        self.robot=robot
        self.instance["BB_uri"]=self.uri_BB
        self.component=conf.Create_skel(self.robot,self.component,self.general,self.instance)

    def start(self):
        self.component["_etc"]["_GENERAL"]=conf.Create_General(self.component)
        Start_Server(self.component)
        #time.sleep(0.3)

    def run(self):
        Run_Server(self.component)
        time.sleep(0.3)

    def stop(self):
        component="{}/{}".format(self.robot_dir,self.component)
        uri_comp = self.BB.Control_Service(component)
        proxy=Proxy(uri_comp)
        if proxy():
            P_Log("[FR][DOWN][FY] Component {}".format(component))
            proxy.shutdown()
        else:
            P_Log("[FR][ERROR][FY] Connecting to Component {} seems Stopped".format(component))

    def status(self):
        component="{}/{}".format(self.robot_dir,self.component)
        uri_comp = self.BB.Control_Service(component)
        proxy=Proxy(uri_comp)
        if proxy():
            proxy.show_PROC()
        else:
            P_Log("[FR][ERROR][FY] Connecting to Component {} seems Stopped".format(component))

    def kill(self):
        component=self.config["_etc"]["name"]
        utils.run_component("component",component,run="kill")
