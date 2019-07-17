#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________


from gevent.server import StreamServer
from PYRobot.libs.interface_control import Control_Interface
from PYRobot.libs.interfaces import Interface
from multiprocessing import Process
import PYRobot.libs.utils as utils
from PYRobot.libs.botlogging.coloramadefs import P_Log
import os
import time
import sys
from PYRobot.libs.proxy import Proxy
from gevent import monkey
monkey.patch_all(thread=False)

def Loader_Config(clss, **kwargs):
    """ Decorator for load configuration into component
        init superclass control
    """
    original_init = clss.__init__

    def init(self):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(clss, self).__init__()
        original_init(self)
    clss.__init__ = init
    return clss

def Start_Server(config):
    servers=[]
    warnings={}
    info=[]
    status=False
    interfaces=config["_etc"]["_INTERFACES"]
    if type(interfaces) not in [tuple,list]:
        interfaces=[interfaces,]
    host=config["_etc"]["ip"]
    port=config["_etc"]["port"]
    name=config["_etc"]["name"]
    cls=config["_etc"]["obj_cls"]
    register= not config["_etc"]["sys"]
    try:
        class_comp=Loader_Config(cls,**config)
        obj=class_comp()
        utils.change_process_name(name)
        obj._PROC["PID"]=os.getpid()
        obj._PROC["status"]=(obj.hello()=="hi")
        if obj._PROC["status"]:
            interfaces.append(Control_Interface)
            for inter in interfaces:
                interface=Interface(inter,obj)
                warnings[interface.__name__]=interface.Not_Implemented
                port=utils.get_free_port(port,host)
                info.append((interface.__name__,"{}:{}".format(host,port)))
                servers.append(StreamServer((host,port), interface()))
                port=port+1
            obj._PROC["info"]=info
            obj._PROC["warnings"]=warnings
            for s in servers[:-1]:
                s.start()
            #obj.set_PROC(status,info,warnings)
            time.sleep(0.3)
            if register:
                obj._Register_Component()
            obj._PROC["SERVER"]=servers[-1]
            obj.show_PROC()
            print("\n\n")
            try:
                #obj.L_info("Starting __Run__ ")
                obj.__Run__()
            except:
                pass
            servers[-1].serve_forever()
            try:
                obj.__Close__()
                #obj.L_info("__Close__ Component")
            except:
                pass
    except KeyboardInterrupt:
        for s in servers:
            s.close()
        try:
            obj.__Close__()
        except:
            pass
        utils.set_tty_out(config["_etc"]["ttydef"])
        P_Log("[FR][DOWN][FY] Starded Component {}".format(name))


    except Exception as ex:
        if status:
            utils.set_tty_out(config["_etc"]["ttydef"])
            P_Log("[FR][DOWN][FY] Starded Component {}".format(name))
            raise
        else:
            utils.set_tty_out(config["_etc"]["ttydef"])
            raise
            P_Log("[FR][ERROR][FY] Starded Component {}".format(name))
            P_Log(str(ex))



def Run_Server(config):
    register= not config["_etc"]["sys"]
    process = Process(target=Start_Server,args=(config))
    process.daemon=True
    process.start()
    return process
