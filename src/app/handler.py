import json
import logging
import time

from paho.mqtt import client as mqtt

from app.homeassistant import config_topic, Device


class Handler(mqtt.Client):

    def __init__(self, app_name: str, devices: list[Device]) -> None:
        super().__init__(client_id=app_name)
        self.devices = devices
        self.retain_status = {d.ha_id: False for d in devices}

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe([(config_topic(d.ha_id), 0) for d in self.devices])

    def on_message(self, client, userdata, msg):
        device_id = msg.topic.split("/")[-2]
        if device_id in self.retain_status:
            self.retain_status[device_id] = True
            logging.debug(f"{device_id} config is already present... Skipping")

    def sync_configs(self):
        for d in self.devices:
            if not self.retain_status[d.ha_id]:
                topic = config_topic(d.ha_id)
                logging.info(f"No retained config for {d.ha_id}. Publishing default.")
                msg = d.serialize()
                self.publish(topic, json.dumps(msg), retain=True)
                time.sleep(0.2)
