#!/usr/bin/env python3
"""Read Alen BreatheSmart air filter values and publish to MQTT"""
import sys
import json
import time
import datetime
import logging
import tinytuya
import paho.mqtt.client as mqttClient

_LOGGER = logging.getLogger(__name__)
FILTER_CONFIG="filter.json"
BROKER_HOST = "localhost"
TOPIC="airfilter/status"

CONNECTED = False # MQTT connected

DPS_MAPPING = {"1": "power",
               "2": "pm2_5",
               "3": "mode",
               "4": "speed",
               "5": "filter_life",
               "6": "ionizer",
               "7": "child_lock"}

def on_connect(client, userdata, flags, code):
    """Connect completion for Paho"""
    _ = client
    _ = userdata
    _ = flags
    global CONNECTED
    if code == 0:
        print("Connected to broker")
        CONNECTED = True                #Signal connection
    else:
        print("Connection failed")

def connect_mqtt():
    """Connect to MQTT"""
    global CONNECTED

    port = 1883

    client = mqttClient.Client("AirFilter")    #create new instance
    client.on_connect = on_connect            #attach function to callback
    client.connect(BROKER_HOST, port=port) #connect to broker

    client.loop_start()

    while not CONNECTED:
        time.sleep(0.1)
    return client

def read_config(filename):
    result = None
    with open(filename) as f:
        result = json.load(f)

    return result

def read_filter(filter):
    """Read filter attributes"""
    device = tinytuya.Device(
        filter['id'], filter['address'], filter['key'])
    device.set_version(3.3)
    raw_status = device.status()
    status = {}
    for key, val in raw_status['dps'].items():
        name = DPS_MAPPING.get(key, key)
        status[name] = val
    return status
    
def publish_result(client, reading, now):
    """Write result to MQTT"""

    message = {"reading": reading,
               "timestamp": str(now)}
    _LOGGER.info("Publish %s", json.dumps(message))
    client.publish(TOPIC, json.dumps(message))

def main(argv):
    """Entry point"""
    _ = argv

    client = connect_mqtt()

    filter = read_config(FILTER_CONFIG)

    while True:
        now = datetime.datetime.now()
        next_time = now + datetime.timedelta(seconds=10)

        reading = None
        for attempt in range(10):
            try:
                reading = read_filter(filter)
                break
            except Exception as e:
                _LOGGER.warning("Exception reading filter: %s", str(e))
                time.sleep(1)

        if reading:
            publish_result(client, reading, now)

        else:
            _LOGGER.warning("Failed to read filter")
        while datetime.datetime.now() < next_time:
            time.sleep(max(datetime.timedelta(seconds=0.1),
                           (next_time - datetime.datetime.now())/2
                           ).total_seconds())

if __name__ == '__main__':
    main(sys.argv[1:])

