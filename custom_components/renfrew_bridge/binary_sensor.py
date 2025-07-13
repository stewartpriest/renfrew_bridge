from datetime import datetime, timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES
from .bridge_status import get_bridge_status

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.info("Renfrew Bridge: async_setup_entry for binary_sensor called")

    refresh_minutes = config_entry.options.get(CONF_REFRESH_MINUTES) or config_entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
    entry_id = config_entry.entry_id

    entities = [RenfrewBridgeBinarySensor("Renfrew Bridge", refresh_minutes, entry_id)]
    async_add_entities(entities)

class TimedUpdateBinarySensor(BinarySensorEntity):
    def __init__(self, name, refresh_minutes, entry_id):
        self._attr_name = name
        self._attr_is_on = None
        self._refresh = timedelta(minutes=refresh_minutes)
        self._last_update = datetime.min
        self._entry_id = entry_id
        slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{slug}"
        self._attr_device_class = "opening"
        self._attr_icon = "mdi:bridge"

    def should_update(self):
        return datetime.now() - self._last_update >= self._refresh

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Renfrew Bridge",
            "manufacturer": "Renfrewshire Council/West Dumbartonshire Council",
            "entry_type": "service"
        }

class RenfrewBridgeBinarySensor(TimedUpdateBinarySensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Binary bridge status sensor received: %s", status)
            self._attr_is_on = not status["bridge_closed"]
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update binary bridge status: %s", e)
            self._attr_is_on = None