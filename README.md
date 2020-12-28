# alen-mqtt
Simple code to read from an Alen BreatheSmart air purifier and publish values via MQTT

## Introduction
Alen BreatheSmart air purifiers have a hidden WiFi interface that implements the Tuya IoT platform. This package polls the purifier via its local port 6668 interface and publishes the values via MQTT, suitable for use in Home Assistant and other home automation.

## Enabling WiFi
To enable WiFi on an Alen BreatheSmart filter:
* Download the "Tuya Smart" app onto your Android or iOS device and create an account
* Hold the "Auto" button for 5-10 seconds or until the WiFi symbol on upper right starts blinking
* Follow the instructions in the Tuya Smart app to scan for and add a device

## Getting local API credentials
Follow the steps at [TuyAPI](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) through running `tuya-cli wizard` to generate an ID and Key. Be forewarned, this process involves setting up a developer account at Tuya but is well documented by the TuyAPI project and relatively straightforward. Note: the 'virtual ID' for the device can be found in the Tuya Smart app's device page under the Edit button (upper right), Device Information.

Note: despite using the process, documentation, and wizard from the TuyAPI project, alen-mqtt uses the semi-related pytuya Python library to talk to the purifier. Once you have the credentials and you're sure it works, you can remove the node.js components if you're not otherwise using them.

## Configuring alen-mqtt
Fill in filter.json with the ID & key from `tuya-cli wizard`, being sure to use the IP address (or hostname) on your local network, not the one reported in the app. You will probably want to configure a static DHCP reservation for your purifier on your router or DHCP server. Change the MQTT `BROKER_HOST` and/or `TOPIC` as required for your setup in `airfilter.py`.

## Running
Just run ./airfilter.py. It should start reading from the purifier and writing to MQTT.

## Home Assistant
Here are the sensors I have created in my own setup:
```
  - platform: mqtt
    name: "Air Purifier"
    state_topic: "airfilter/status"
    value_template: "{{ value_json.reading.pm2_5 }}"
    json_attributes_topic: "airfilter/status"
    json_attributes_template: "{{ value_json.reading | tojson }}"
    unit_of_measurement: "μg/m^3"
  - platform: template
    sensors:
      air_purifier_speed:
	friendly_name: "Air Purifier Fan Speed"
        value_template: "{{ states.sensor.air_purifier.attributes['speed'] }}"
      air_purifier_filter_life:
        friendly_name: "Air Purifier Filter Life"
	value_template: "{{ states.sensor.air_purifier.attributes['filter_life'] }}"
        unit_of_measurement: '%'
```

## DPS fields
I have figured out the obvious field mappings from the raw `dps` dict. They are documented here for completeness.

`{'devId': '<id>', 'dps': {'1': True, '2': 1, '3': 'Auto', '4': '2', '5': 73, '6': True, '7': False, '17': 127860, '19': '0', '21': 0}}`

|dps| meaning|
|---| -------|
|1  |  power         |
|2  |  pm2.5, μg/m^3 |
|3  |  mode (Auto, Manual, Sleep) |
|4  |  fan speed     |
|5  |  Filter percent remaining |
|6  |  ionizer       |
|7  |  lock          |
|17 | ? |
|19 | ? |
|21 | ? |

I'm not sure what the last 3 fields represent.