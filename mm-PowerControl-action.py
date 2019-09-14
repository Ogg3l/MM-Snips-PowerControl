# !/usr/bin/env python
# encoding: utf-8
import paho.mqtt.client as mqtt 
import json

def on_connect(client, userdata, flags, rc): 
    print('Connected') 
    mqtt.subscribe('hermes/intent/Oggel:MonitorPowerOff')

def on_message(client, userdata, msg):
    # Parse the json response
    intent_json = json.loads(msg.payload)
    intentName = intent_json['intent']['intentName']
    slots = intent_json['slots']
    print('Intent {}'.format(intentName))
    for slot in slots:
        slot_name = slot['slotName']
        raw_value = slot['rawValue']
        value = slot['value']['value']
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_name, raw_value, value))
        
mqtt = mqtt.Client() 
mqtt.on_connect = on_connect
mqtt.on_message = on_message
mqtt.connect('pimirror', 1883) 
mqtt.loop_forever()
