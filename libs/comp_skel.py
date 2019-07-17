
from PYRobot.libs import utils

ttydef,ttyout,ttyerr =utils.assing_ttys()
eths_available = utils.get_all_ip_eths()
ethernet = utils.get_interface()
ip = utils.get_ip_address(ethernet)
host = utils.get_host_name()
broadcast_port=9999


General_Skel={
    "robot":None,
    "sys":False,
    "KEY":"key:user",
    "port":4040,
    "MQTT_port":1883,
    "MQTT_uri":"0.0.0.0:0",
    "broadcast_port":9999,
    "BB_uri":"0.0.0.0:0",
    "logging_level":50,
    "def_worker":True,
    "frec":0.2,
    "mode":"public",
    "public_sync":False,
    "running":False
}

Component_Skel={
"_etc":{
    "name":"Noname",
    "host":host,
    "component":None,
    "robot":"PYRobot",
    "dir_comp":"",
    "cls":None,
    "obj_cls":None,
    "sys":False,
    "KEY":"key:user",
    "ethernet":ethernet,
    "ip":ip,
    "port":4040,
    "MQTT_port":1883,
    "broadcast_port":broadcast_port,
    "ttydef":ttydef,
    "ttyout":ttyout,
    "ttyerr":ttyerr,
    "running":"stop",
    "def_worker":True,
    "frec":0.2,
    "mode":"public",
    "public_sync":False,
    "BB_uri":None,
    "MQTT_uri":None,
    "eths":eths_available,
    "logging_level":50,
    "_INTERFACES":[],
    "_REQ":{},
    "_PUB":[],
    "_SUB":{},
    "_PUB_EVENTS":{},
    "_SUB_EVENTS":{}
    },
"_PROC":{
    "status":None,
    "pid":None,
    "info":None,
    "warnings":[],
    "BB_proxy":None,
    "PUB":None,
    "SUB":None,
    "CONTROL":None
    },
"DOCS":{}
}

_OPTIONS=[k for k in Component_Skel["_etc"] if k[0]=="_" ]+["_LOCAL_CONFIG"]
