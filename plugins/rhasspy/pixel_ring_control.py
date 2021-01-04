#!/usr/bin/env python3

import os
import time
import usb.core
import usb.util
import paho.mqtt.client as paho

MQTTHOST        = os.getenv('RHASSPY_MQTTHOST', '127.0.0.1')
MQTTPORT        = int(os.getenv('RHASSPY_MQTTPORT', 12183))
MQTTUSERNAME    = os.getenv('RHASSPY_MQTTUSERNAME', None)
MQTTPASSWORD    = os.getenv('RHASSPY_MQTTPASSWORD', None)

RHASSPY_MQTT_DIALOG_STARTED_TOPIC = 'hermes/hotword/default/detected'
RHASSPY_MQTT_DIALOG_ENDED_TOPIC = 'hermes/dialogueManager/sessionEnded'
RHASSPY_MQTT_TTS_STARTED_TOPIC = 'hermes/tts/say'
RHASSPY_MQTT_TTS_ENDED_TOPIC = 'hermes/tts/sayFinished'

class PixelRing:
    TIMEOUT = 8000

    def __init__(self, dev):
        self.dev = dev

    def trace(self):
        self.write(0)

    def mono(self, color):
        self.write(1, [(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, 0])
    
    def set_color(self, rgb=None, r=0, g=0, b=0):
        if rgb:
            self.mono(rgb)
        else:
            self.write(1, [r, g, b, 0])

    def off(self):
        self.mono(0)

    def listen(self, direction=None):
        self.write(2)

    wakeup = listen

    def speak(self):
        self.write(3)

    def think(self):
        self.write(4)

    wait = think

    def spin(self):
        self.write(5)

    def show(self, data):
        self.write(6, data)

    customize = show
        
    def set_brightness(self, brightness):
        self.write(0x20, [brightness])
    
    def set_color_palette(self, a, b):
        self.write(0x21, [(a >> 16) & 0xFF, (a >> 8) & 0xFF, a & 0xFF, 0, (b >> 16) & 0xFF, (b >> 8) & 0xFF, b & 0xFF, 0])

    def set_vad_led(self, state):
        self.write(0x22, [state])

    def set_volume(self, volume):
        self.write(0x23, [volume])

    def change_pattern(self, pattern=None):
        print('Not support to change pattern')

    def write(self, cmd, data=[0]):
        self.dev.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, cmd, 0x1C, data, self.TIMEOUT)

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.dev)


def find(vid=0x2886, pid=0x0018):
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if not dev:
        return

    return PixelRing(dev)

pixel_ring = find()
pixel_ring.off()

topics = {
    'hermes/hotword/default/detected': pixel_ring.listen,
    'hermes/dialogueManager/sessionEnded': pixel_ring.off,
    'hermes/tts/sayFinished': pixel_ring.trace,
    'hermes/asr/textCaptured': pixel_ring.spin,
    'hermes/nlu/intentNotRecognized': pixel_ring.off
}

def on_message(client, userdata, message):
    print(message.topic)
    if message.topic in topics:
        function_to_execute = topics.get(message.topic)
        function_to_execute()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    clientid = 'pixel-ring-%s' % os.getpid()
    mqtt = paho.Client(clientid, clean_session=True)
    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    if MQTTUSERNAME is not None or MQTTPASSWORD is not None:
        mqtt.username_pw_set(MQTTUSERNAME, MQTTPASSWORD)

    mqtt.connect(MQTTHOST, MQTTPORT)

    return mqtt

mqtt = connect_mqtt()
mqtt.loop_start()

mqtt.subscribe("hermes/nlu/#")
mqtt.subscribe("hermes/tts/#")
mqtt.subscribe("hermes/handle/#")
mqtt.subscribe("hermes/error/#")
mqtt.subscribe("hermes/hotword/#")
mqtt.subscribe("hermes/dialogueManager/#")
mqtt.subscribe("hermes/asr/#")

print("Subscribed to RHASSPY MQTT Topics!")

while True:
    time.sleep(1000)
