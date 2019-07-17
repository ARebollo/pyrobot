import time
import paho.mqtt.publish as pub
from  threading import Thread
from PYRobot.libs.utils import get_ip_port
from PYRobot.libs.botlogging.coloramadefs import P_Log
import json

class Publication(object):

    def __init__(self,component,mqtt_uri,obj,sync=True,frec=0.1,qos=0):
        self._host,self._port=get_ip_port(mqtt_uri)
        if len(component.split("/"))==2:
            self._robot,self._comp=component.split("/")
        else:
            self._robot="ALL"
            self._comp=component
        self._qos=qos
        self.topics=set()
        self.events={}
        self.sync=sync
        self.obj=obj
        self.frec=frec
        self.work=True
        self.pre= str(component) + "/"

    def add_topics(self,*topics):
        for n in topics:
            if hasattr(self.obj,n):
                self.topics.add(n)
            else:
                P_Log("{} not registered".format(n))

    def get_topics(self):
        return list(self.topics)

    def get_events(self):
        return [x for x in self.events]

    def add_event(self,entity,event):
        try:
            name,fn=event.split("::")
            self.events.setdefault(entity,[])
            fn=fn.replace("self.","self.obj.")
            self.events[entity].append((name,fn))
            #print("Pub events",self.events)
        except:
            P_Log("error loading {}".format(event))

    def check(self,fn):
        try:
            return eval(fn)
        except Exception as ex:
            #print(str(ex))
            return "ERR"

    def Pub_events(self):
        for entity,events in self.events.items():
            send_events=[k for k,v in events if self.check(v)==True]
            #err_evensts=[k for k,v in events if self.check(v)=="ERR"]
            if len(send_events)>0:
                payload_value =json.dumps([send_events,"E",time.time()])
                topic=self.pre+entity
                #print("event",topic,payload_value)
                pub.single(topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)

    def Pub_single(self,topic):
        if hasattr(self.obj,topic):
            data=getattr(self.obj,topic)
            payload_value =json.dumps([data,"V",time.time()])
            topic=self.pre+topic
            #print("publication",topic,payload_value)
            pub.single(topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)

    def Pub(self):
        if not self.sync:
            for n in self.topics:
                self.Pub_single(n)
            self.Pub_events()
        else:
            P_Log("start active")

    def _Do_Pub(self):
        while self.work:
            for n in self.topics:
                self.Pub_single(n)
                self.Pub_events()
            time.sleep(self.frec)

    def stop(self):
        self.work=False

    def change_frec(self,frec):
        if frec>0:
            self.frec=frec

    def start(self):
        if self.sync:
            self.work=True
            self.thread=Thread(target=self._Do_Pub,name=self._comp+":PUB")
            self.thread.setDaemon(True)
            self.thread.start()
        else:
            P_Log("Mode asyncronous activate")
