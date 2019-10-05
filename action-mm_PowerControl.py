#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import paho.mqtt.client as mqtt
import json


#From Template
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"



app_name = "MM-PowerControl"
external_topic = "external/MagicMirror2/VoiceControl"


#Names of Intents and Slots
intent_powercontrol = "PowerControl"
intent_2 = "Intent2"

#Config from Intent Names
intent_dic = {
    intent_powercontrol : {
                            "slot_device" : "device",
                            "slot_power" : "power"

                        },
    
    intent_2            : {
                            "slot_1" : "slot1",
                            "slot_2" : "slot2"
                        }   
}


#MQTT Client
mqtt_client = mqtt.Client()


#Config Functions from template
class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()



def on_connect(client, userdata, flags, rc): 
    print('Connected') 
    mqtt_client.subscribe('hermes/intent/Oggel:MonitorPowerOff')
    mqtt_client.subscribe('hermes/intent/Oggel:MonitorPowerOn')
    mqtt_client.subscribe('hermes/intent/Oggel:PowerControl')

def on_message(client, userdata, msg):
    # Parse the json response
    intent_json = json.loads(msg.payload.decode("utf-8"))
    session_id = intent_json['sessionId']
    intentName = intent_json['intent']['intentName'].split(':')[1]
    slots = intent_json['slots']
    print('Intent {}'.format(intentName))


    #For Intent PowerControl    
    if(intentName == intent_powercontrol):
        device = ""
        power = ""

        #Go through slots
        for slot in slots:
            slot_name = slot['slotName']
            #raw_value = slot['rawValue']
            value = slot['value']['value']
            print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_name, raw_value, value))

            if(slot_name == intent_dic[intent_powercontrol]["slot_device"]):
                device = value
            elif(slot_name == intent_dic[intent_powercontrol]["slot_power"]):
                power = value

        #Create Dictionary and Publish
        #publish_dic = {device : power}
        if(device == "pi" and power == "an"):
            say(sesssion_id,"Das kann ich leider nicht")
        
        else:
            publish_dic = {'device' : device, 'power' : power}
            say(session_id,"Alles klar")
            mqtt_client.publish((external_topic),json.dumps(publish_dic))


def say (session_id, text):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text' : text, 'sessionId' : session_id}))
                                
if __name__ == "__main__":        
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883) 
    mqtt_client.loop_forever()
