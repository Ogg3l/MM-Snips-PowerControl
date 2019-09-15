# !/usr/bin/env python3
# encoding: utf-8
import configparser
import io
import paho.mqtt.client as mqtt 
import json



CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

app_name = "MM-PowerControl"
external_topic = "external/MagicMirror2/VoiceControl"

#Names of Intents and Slots
intent_powercontrol = "PowerControl"
intent_2 = "Intent2"

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
    intentName = intent_json['intent']['intentName'].split(':')[1]
    slots = intent_json['slots']
    #print('Intent {}'.format(intentName))

    if(intentName == intent_powercontrol):
        device = slots[0]["value"]["value"]
        action = slots[1]["value"]["value"]

        
        publish_dic = {device : action}
        mqtt_client.publish((external_topic),json.dumps(publish_dic))

    '''
    for slot in slots:
        slot_name = slot['slotName']
        raw_value = slot['rawValue']
        value = slot['value']['value']
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_name, raw_value, value))
    '''
        
                                
if __name__ == "__main__":        
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883) 
    mqtt_client.loop_forever()
