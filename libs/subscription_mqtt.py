import paho.mqtt.client as mqtt
import time
from  threading import Thread
from PYRobot.libs.utils import get_ip_port
import json


class subscriptions(object):
    def __init__(self,robot,uri,obj=None):
        self._host,self._port=get_ip_port(uri)
        self._qos=0
        if len(robot.split("/"))==2:
            self._robot,self._comp=robot.split("/")
        else:
            self._robot="ALL"
            self._comp=robot
        self.topics={}
        self.events={}
        self.obj=obj
        self.client = mqtt.Client()
        self.client.on_message=self.on_message
        self.client.connect(host=self._host, port=self._port, keepalive=60)
        self.client.loop_start()

    def connect(self):
        topics=[(proxy,self._qos) for proxy in self.topics]
        events=[(proxy,self._qos) for proxy in self.events]
        self.client.subscribe(topic=topics+events)

    def loop(self):
        self.client.loop()

    def subscribe_topics(self,**topics):
        for item,proxy in topics.items():
            self.topics[proxy]=item
            if item not in self.obj.__dict__:
                setattr(self.obj,item,None)

    def subscribe_events(self,**events):
        for item,proxy in events.items():
            self.events[proxy]=[item,None]
            if item not in self.obj.__dict__:
                setattr(self.obj,item,[])

    def get_topics(self):
        return list(self.topics.values())

    def get_events(self):
        return list(self.events)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def add_handler(self,event,handler):
        events=[k for k,v in self.events.items() if v[0]==event]
        if len(events)==1:
            ev=events[0]
            self.events[ev][1]=handler

    def on_message(self,client, userdata, msg):
        if self.obj is not None:
            value=json.loads(msg.payload.decode())
            if value[1]=="V":
                item=self.topics[msg.topic]
                setattr(self.obj,item,value[0])
            if value[1]=="E":
                item=self.events[msg.topic][0]
                setattr(self.obj,item,value[0])
                handler=self.events[msg.topic][1]
                if handler is not None:
                    try:
                        handler(item,value[0])
                    except Exception as es:
                        print(es)
