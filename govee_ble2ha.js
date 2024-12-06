let devices = [
    {
        "id": "01",
        "mac": "A4:C1:38:EC:C6:28",
        "location": "Living Room"
    }, {
        "id": "02",
        "mac": "A4:C1:38:00:5D:34",
        "location": "Babyroom"
    }, {
        "id": "03",
        "mac": "A4:C1:38:4C:B8:0C",
        "location": "Bedroom"
    }, {
        "id": "04",
        "mac": "A4:C1:38:95:43:B3",
        "location": "Kitchen"
    }
];

function setup_devices(){
    for (let i = 0; i < devices.length; i++) {
        let device = devices[i];
        config_message = {
            "state_topic": "govee/" + device.id  + "/state",
            "device": {
                "identifiers": ["govee_" + device.id],
                "name": "Sensor " + device.location,
                "manufacturer": "Govee",
                "model": "H5075"
            },
            "origin": {
                "name": "ble2mqtt"
            },
            "components": {
                "temperature": {
                    "name": "Temperature",
                    "platform": "sensor",
                    "unique_id": "govee_" + device.id + "_temp",
                    "device_class": "temperature",
                    "unit_of_measurement": "°C",
                    "icon": "mdi:thermometer",
                    "suggested_display_precision": 1,
                    "value_template": "{{ value_json.temperature }}"
                },
                "humidity": {
                    "name": "Humidity",
                    "platform": "sensor",
                    "unique_id": "govee_" + device.id + "_hum",
                    "device_class": "humidity",
                    "unit_of_measurement": "%",
                    "icon": "mdi:water-percent",
                    "suggested_display_precision": 0,
                    "value_template": "{{ value_json.humidity }}"
                },
                "battery": {
                    "name": "Battery",
                    "platform": "sensor",
                    "unique_id": "govee_" + device.id + "_battery",
                    "device_class": "battery",
                    "unit_of_measurement": "%",
                    "icon": "mdi:battery-30",
                    "suggested_display_precision": 0,
                    "value_template": "{{ value_json.battery }}"
                },
                "rssi": {
                    "name": "Signal Strength",
                    "platform": "sensor",
                    "unique_id": "govee_" + device.id + "_rssi",
                    "device_class": "signal_strength",
                    "unit_of_measurement": "dBm",
                    "icon": "mdi:signal",
                    "suggested_display_precision": 0,
                    "value_template": "{{ value_json.rssi }}"
                }
            }
        };
        let topic = "homeassistant/device/govee_" + device.id + "/config";
        MQTT.publish(topic, JSON.stringify(config_message), retain=true);
    }
}

setup_devices()

BLE.Scanner.Start(
  options={duration_ms: 5000, active: true},
  callback=function(event, result) {
    if (event === BLE.Scanner.SCAN_RESULT) {
      for (let i = 0; i < devices.length; i++) {
        if (devices[i].mac.toLowerCase() === result.addr) {
          let measurements = readGovee(result);
          let topic = "govee/" + devices[i].id  + "/state";
          MQTT.publish(topic, JSON.stringify(measurements), retain=false);
        }
      }
    }
});

function readGovee(result){
  let data = result.manufacturer_data["ec88"];
  if (data.length === 6) {
    let basenum = (data.charCodeAt(1) << 16) | (data.charCodeAt(2) << 8) | data.charCodeAt(3);
    let measurements = {
        "temperature": basenum / 10000.0,
        "humidity": (basenum % 1000) / 10.0,
        "battery": data.charCodeAt(4) / 1.0,
        "rssi": result.rssi
    };
    return measurements;
  }
}