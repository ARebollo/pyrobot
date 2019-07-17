#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________
#from libs import utils
from gevent import monkey
monkey.patch_all(thread=False)
import time
import threading
import os
from threading import Thread
from termcolor import colored
from PYRobot.libs.botlogging import botlogging
import PYRobot.libs.utils as utils
from PYRobot.libs.proxy import Proxy
from PYRobot.libs.publication_mqtt import Publication
from PYRobot.libs.subscription_mqtt import subscriptions

RETRYS=50

def threaded(fn):
    """To use as decorator to make a function call threaded."""

    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args,name=fn.__name__, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def connect_component(obj):
    obj._PROC["running"]="stop"
    obj.worker_run=obj._etc.get("def_worker",True)
    obj._PROC["BB_proxy"]=Proxy(obj._etc["BB_uri"])
    #loading topics and events
    name=obj._etc["name"]
    robot=obj._etc["robot"]
    uri=obj._etc["MQTT_uri"]
    sync=obj._etc["public_sync"]
    frec=obj._etc["frec"]

    #loading publications
    if len(obj._etc["_PUB"])+len(obj._etc["_PUB_EVENTS"])>0:
        obj._PROC["PUB"]=Publication(name,uri,obj,sync,frec)
        obj._PROC["PUB"].add_topics(*obj._etc["_PUB"])
        for ent,events in obj._etc["_PUB_EVENTS"].items():
            for e in events:
                obj._PROC["PUB"].add_event(ent,e)
        if sync:
            obj._PROC["PUB"].start()
    #conectar subcriptores
    name=obj._etc["name"]
    uri=obj._etc["MQTT_uri"]
    if len(obj._etc["_SUB"])+len(obj._etc["_SUB_EVENTS"])>0:
        obj._PROC["SUB"]=subscriptions(name,uri,obj)
        topics={x:k.replace("LOCAL/",robot+"/")
                  for x,k in obj._etc["_SUB"].items()}
        obj._PROC["SUB"].subscribe_topics(**topics)
        events={x:k.replace("LOCAL/",robot+"/")
                  for x,k in obj._etc["_SUB_EVENTS"].items()}
        obj._PROC["SUB"].subscribe_events(**events)
        obj._PROC["SUB"].connect()

    #lanzar proxys remotes y locales _REQ_INTERFACES HECHO
    req={x:k.replace("LOCAL/",robot+"/")
              for x,k in obj._etc["_REQ"].items()}
    obj._PROC["running"]="WAITING REQUIRES"
    name=obj._etc["name"]+".conectors"
    t = threading.Thread(target=_conectors,args=(obj,req,),name=name)
    t.setDaemon(True)
    t.start()

def _conectors(obj,reqs):
    #importante : dentro de los threads no podemos acceder a proxys externos
    # gevent no funciona bien en el intercambio con thread
    # solucion crear el proxy dentro.]
    items=list(reqs)
    BB_name=Proxy(obj._etc["BB_uri"])
    BB_name.connect()
    while obj._PROC["running"]!="RUNNING":
        retrys=RETRYS
        while items!=[] and retrys>0:
            item=items.pop()
            uri=BB_name.Get_Interface_Uri(reqs[item])
            if uri=="0.0.0.0:0":
                items.append(item)
                time.sleep(0.3)
            else:
                obj.L_info("{} connect to {}".format(item,uri))
                setattr(obj,item,uri)
            retrys=retrys-1
        if items==[]:
            obj._PROC["running"]="RUNNING"
        else:
            obj.L_info("Error connecting {}".format(items))

# Class control component
class Control(botlogging.Logging):
    """ This class provide threading funcionality to all object in node.
        Init workers Threads and PUB/SUB thread"""

    def __init__(self):
        super().__init__()
        self.set_ttys()
        connect_component(self)

    def start_worker(self, fn, *args):
        """ Start all workers daemon"""
        self._PROC["workers"]=[]
        if type(fn) not in (list, tuple):
            fn = (fn,)
        if self.worker_run:
            for func in fn:
                self.start_thread(func,*args)

    def start_thread(self, fn, *args):
        """ Start all workers daemon"""
        if self.worker_run:
            name=self._etc["name"]+"."+fn.__name__
            t = threading.Thread(target=fn,name=name, args=args)
            t.setDaemon(True)
            self._PROC["workers"].append(t)
            self.L_info("{} worker Started".format(fn.__name__))
            t.start()


    def set_PROC(self,status,info,warnings):
        self._PROC["status"]=status
        self._PROC["pid"]=os.getpid()
        self._PROC["info"]=info
        self._PROC["warnings"]=warnings

    def show_PROC(self,all=True):
        utils.set_tty_out(self._etc["ttydef"])
        #self.L_print("")
        if self._PROC["status"]:
            self.L_print("[FG] [OK][FY] Starded Component {}".format(self._etc["name"]))
            self.L_print("\t Network:{} Host: {} Pid:{}".
                    format(self._etc["ethernet"],self._etc["host"],self._PROC["PID"]))
            if all:
                for t in self._PROC["info"]:
                    self.L_print("\t {} {}".format(t[1],t[0]))
                    for w in self._PROC["warnings"][t[0]]:
                        self.L_print("\t\t Warning: {} not implemented".format(w))
                if self._PROC["PUB"] is not None:
                    t=self._PROC["PUB"].get_topics()
                    if len(t)>0:
                        self.L_print("\t Publicating Topics: {}".format(t))
                    t=self._PROC["PUB"].get_events()
                    if len(t)>0:
                        self.L_print("\t Publicating Events channels: {}".format(t))
                if self._PROC["SUB"] is not None:
                    t=self._PROC["SUB"].get_topics()
                    if len(t)>0:
                        self.L_print("\t subscriptions Topics: {}".format(t))
                    t=self._PROC["SUB"].get_events()
                    if len(t)>0:
                        self.L_print("\t subscribe Events channels: {}".format(t))
                self.L_print("\t Status: {}".format(self._PROC["running"]))
            #self.L_print("")
        else:
            self.L_print("[FR][ERROR][FY] Starded Component dd{}".format(self._etc["name"]))
            #self.L_print("")
        utils.set_tty_out(self._etc["ttyout"])

    def _Register_Component(self):
        if self._PROC["BB_proxy"].connect():
            comp={}
            comp["PID"]=os.getpid()
            comp["host"]=self._etc["host"]
            comp["INTERFACES"]=self._PROC["info"]
            comp["PUB"]=self._etc["_PUB"]
            comp["SUB"]=self._etc["_SUB"]
            events=list(self._etc["_PUB_EVENTS"].keys())
            comp["EVENTS"]=events
            comp["GENERAL"]=self._etc["_GENERAL"]
            del(self._etc["_GENERAL"])
            self._PROC["BB_proxy"].Register_Comp(self._etc["name"],comp)

    def New_handler(self,event,handler):
        if self._PROC["SUB"] is not None:
            self._PROC["SUB"].add_handler(event,handler)


    def get_PROC(self):
        return self._PROC

    def shutdown(self):
        self._PROC["SERVER"].stop()

    def hello(self):
        return "hi"

    def get_ttys(self):
        return self._etc["ttyout"],self._etc["ttyerr"]

    def set_ttys(self):
        utils.set_tty_out(self._etc["ttyout"])
        utils.set_tty_err(self._etc["ttyerr"])

    def get_name(self):
        return self._etc["name"]
