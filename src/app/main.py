import time

from app.homeassistant import load_devices
from app.handler import Handler
from app.settings import settings


def main():
    devices = load_devices()
    client = Handler("hass-healthcheck", devices=devices)
    client.connect(settings.broker_uri)

    client.loop_start()
    time.sleep(settings.timeout)

    client.sync_configs()
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
