
import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

from custom_components.renfrew_bridge.bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([
        RenfrewBridgeStatusSensor("Renfrew Bridge Status"),
        RenfrewBridgeNextClosureSensor("Renfrew Bridge Next Closure")
    ])


class RenfrewBridgeStatusSensor(Entity):
    def __init__(self, name):
        self._name = name
        self._state = None
        self._attr_icon = "mdi:bridge"

    @Throttle(SCAN_INTERVAL)
    def update(self):
        try:
            status = get_bridge_status()
            self._state = "closed" if status['bridge_closed'] else "open"
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge status: %s", e)
            self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state


class RenfrewBridgeNextClosureSensor(Entity):
    def __init__(self, name):
        self._name = name
        self._state = None
        self._attr_icon = "mdi:calendar-clock"

    @Throttle(SCAN_INTERVAL)
    def update(self):
        try:
            status = get_bridge_status()
            self._state = status['next_closure_start']
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge next closure: %s", e)
            self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
