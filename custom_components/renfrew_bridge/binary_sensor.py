import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Renfrew Bridge binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [RenfrewBridgeBinarySensor(coordinator, "Renfrew Bridge")]
    async_add_entities(entities)

class RenfrewBridgeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for the Renfrew Bridge status."""

    def __init__(self, coordinator, name):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._entry_id = coordinator.config_entry.entry_id
        slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{self._entry_id}_{slug}"
        self._attr_device_class = "opening"
        self._attr_icon = "mdi:bridge"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        data = self.coordinator.data
        if not data:
            return None
        return not data["bridge_closed"]

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Renfrew Bridge",
            "manufacturer": "Renfrewshire Council/West Dumbartonshire Council",
            "entry_type": "service"
        }