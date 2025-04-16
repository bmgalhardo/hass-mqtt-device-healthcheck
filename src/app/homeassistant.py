import yaml

from enum import auto, StrEnum
from slugify import slugify
from pathlib import Path
from pydantic import BaseModel, Field


class EntityCategory(StrEnum):
    CONFIG = auto()
    DIAGNOSTIC = auto()


class StateClass(StrEnum):
    MEASUREMENT = auto()
    TOTAL = auto()


class Component(BaseModel):
    name: str
    platform: str
    device_class: str  # https://www.home-assistant.io/integrations/homeassistant/#device-class
    state_class: StateClass = StateClass.MEASUREMENT
    unit_of_measurement: str | None = None
    icon: str
    suggested_display_precision: int = 0
    value_template: str
    entity_category: EntityCategory | None = None
    event_types: list[str] | None = None
    state_topic: str | None = None

    def serialize(self, ha_id: str) -> dict:
        message = self.model_dump(exclude_none=True)
        message["unique_id"] = f"{ha_id}_{slugify(self.name)}"
        return message


class Device(BaseModel):
    ha_id: str = Field(alias="id")
    manufacturer: str | None = None
    model: str | None = None
    sw_version: str | None = None
    name: str
    mac_addr: str | None = None
    origin: str
    components: list[Component]
    state_topic: str | None = None

    def default_state_topic(self):
        return f"devices/{self.ha_id}/state"

    def serialize(self):
        return {
            "state_topic": self.default_state_topic() if self.state_topic is None else self.state_topic,
            "device": {
                "identifiers": [self.ha_id],
                "name": self.name,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "connections": [["mac", self.mac_addr]] if self.mac_addr else [],
            },
            "origin": {"name": self.origin},
            "components": {slugify(comp.name): comp.serialize(self.ha_id) for comp in self.components},
        }


def load_devices() -> list[Device]:
    path = Path(__file__).resolve().parent
    with open(path / "devices.yml", "r") as file:
        yml_file = yaml.safe_load(file)
    devices = [Device(**d) for d in yml_file.get("devices")]
    return devices


def config_topic(ha_id: str):
    return f"homeassistant/device/{ha_id}/config"
