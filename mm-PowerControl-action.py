# !/usr/bin/env python3
# encoding: utf-8
import paho.mqtt.client as mqtt 
import json

app_name = "MM-PowerControl"
external_topic = "external/MagicMirror2/PowerControl/"

intent_monitorOff = "MonitorPowerOff"
intent_monitorOn = "MonitorPowerOn"
intent_piOff = "piOff"

mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc): 
    #print('Connected') 
    mqtt_client.subscribe('hermes/intent/Oggel:MonitorPowerOff')
    mqtt_client.subscribe('hermes/intent/Oggel:MonitorPowerOn')

def on_message(client, userdata, msg):
    # Parse the json response
    intent_json = json.loads(msg.payload.decode())
    intentName = intent_json['intent']['intentName'].split(':')[1]
    slots = intent_json['slots']
    #print('Intent {}'.format(intentName))

    #Device Monitor or RasPi
    device = ""
    #Dictionary which is published
    actionDic = {}
    
    for slot in slots:
        slot_name = slot['slotName']
        raw_value = slot['rawValue']
        value = slot['value']['value']
        #print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_name, raw_value, value))

        if(slot_name == "monitor"):
            actionDic[slot_name] = ""
            device = slot_name
        elif(slot_name == "an" or slot_name == "aus"):
            actionDic[device] = slot_name

    #Publish 
    if (intentName == intent_monitorOff):
            mqtt_client.publish((external_topic + intentName),json.dumps(actionDic))
    elif (intentName == intent_monitorOn):
            mqtt_client.publish((external_topic + intentName),json.dumps(actionDic))
                                
if __name__ == "__main__":        
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883) 
    mqtt_client.loop_forever()
