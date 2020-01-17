#!/usr/bin/python
#coding=utf-8
import paho.mqtt.client as mqtt
import time
import json
import RPi.GPIO as GPIO

Connected = False #global variable for the state of the connection
RATIO = 5 # global variable for alcohol ratio (scale 0 - 10)

broker_address = "localhost"
port = 1883
user = "pi"
#password = "raspberry"

GPIO.setmode(GPIO.BCM)

# pins dict
pins = {
    #23: {"name": "GPIO 23", "state": GPIO.LOW},
    "air_pump": {"pin": 21, "name": "GPIO 29", "default_state": GPIO.LOW},
    "alc": {"pin": 20, "name": "GPIO 28", "default_state": GPIO.LOW},
    "mixer": {"pin": 16, "name": "GPIO 27", "default_state": GPIO.LOW},
}

def reset_pins():
    """Reset pins"""
    print("resetting pins")
    for pin_name, pin_info in pins.items():
        pin = pin_info["pin"]
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, pin_info["default_state"])

# The callback for when the client receives a CONNACK response from the server.
def on_connect(self, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")

# The callback for when a PUBLISH message is received from the server.
def listener(self, userdata, msg):
    try:
        message = json.loads(msg.payload)
        # Make_drink
        if(message['action'] == "toggle"):
            make_drink(self)
            print("pushing toggle (make a drink)")
        # Decrease alc_level
        elif(message['action'] == "brightness_down_click"):
            alc_ratio(self, 0)
            print("pushing brightness_down_click (alc_ratio decrease)")
        # Increase alc_level
        elif(message['action'] == "brightness_up_click"):
            alc_ratio(self, 1)
            print("pushing brightness_up_click (alc_ratio increase)")
        # Reset alc_level
        elif(message['action'] == "arrow_left_click" or message['action'] == "arrow_right_click"):
            alc_ratio(self, 2)
            print("pushing arrow_left_click (reset)")
        else:
            print("unknown button signal")
    except Exception as e:
        print("Exception: " + e)

def make_drink(self):
    """Make a drink"""
    # pump on = red led on
    reset_pins()

    print("The pump is ON")
    GPIO.output(pins["air_pump"]["pin"], GPIO.HIGH)
    time.sleep(1)
    # alcohol = yellow led on
    GPIO.output(pins["alc"]["pin"], GPIO.HIGH)
    print("Alcohol valve is open")
    time.sleep(RATIO)
    GPIO.output(pins["alc"]["pin"], GPIO.LOW)
    print("Alcohol valve is closed")
    
    # mixer = green led on
    GPIO.output(pins["mixer"]["pin"], GPIO.HIGH)
    print("Mixer valve is open")
    # fix this hardcoded 10
    time.sleep(10 - RATIO)
    GPIO.output(pins["mixer"]["pin"], GPIO.LOW)
    print("Mixer valve is closed")

    #pump off
    GPIO.output(pins["air_pump"]["pin"], GPIO.LOW)
    print("Pump off")
    sender(self, 1) # drink done

# Create and publish message to the server
def sender(self, action, brightness=254):
    if action == 1: # Drink done, flash the lamp
        self.publish("zigbee2mqtt/IKEA_LAMP/set", create_payload("TOGGLE"))
        time.sleep(2)
        self.publish("zigbee2mqtt/IKEA_LAMP/set", create_payload("TOGGLE"))
    elif action == 2: # Adjust the brightness of the lamp
        self.publish("zigbee2mqtt/IKEA_LAMP/set", create_payload("ON", brightness))
    else:
        print("Cannot publish message, unkown action")
        
def create_payload(lamp_state, brightness_value=254):
    # Lamp_state "TOGGLE" runs only without brightness value)
    if lamp_state == "TOGGLE":
        payload = '{"state":"TOGGLE"}'
    else:
        payload = '{"state":"' + str(lamp_state) + '", "brightness":"' + str(brightness_value) + '"}'
    return payload

def alc_ratio(self, ratio_action):
    """Set alcohol ratio"""
    global RATIO
    #brightness ratio * 25 needs to be tweaked
    if ratio_action == 1:
        if RATIO < 10:
            RATIO += 1
    elif ratio_action == 0:
        if RATIO > 0:
            RATIO -= 1
    elif ratio_action == 2:
        RATIO = 5
    sender(self, 2, RATIO * 25)

def on_publish(self, userdata, msg):
    print("data published \n")

def main():
    client = mqtt.Client()
    client.username_pw_set(user, password=None)
    client.on_connect = on_connect # Create connection to the server
    client.on_message = listener # Open received message from the server
    client.on_publish = on_publish # Get acknowledgement that publishment has done

    client.connect(broker_address, port = port)
    client.loop_start()
    client.subscribe([("zigbee2mqtt/IKEA_SWITCH", 0), ("zigbee2mqtt/IKEA_LAMP", 0)]) # Params: topic name and qos level

    while Connected != True: # Poll the server until the connection is established
        time.sleep(0.1)

    try:
        while True: # Keep the script running until interrupted
            time.sleep(1)
    except KeyboardInterrupt:
        print("exiting")
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    main()