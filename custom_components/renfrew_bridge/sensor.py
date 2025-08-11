import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Renfrew Bridge sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        RenfrewBridgeStatusSensor(coordinator, "Renfrew Bridge Status"),
        RenfrewBridgeNextClosureStartsPrettySensor(coordinator, "Renfrew Bridge Next Closure Starts (Pretty)"),
        RenfrewBridgeNextClosureEndsPrettySensor(coordinator, "Renfrew Bridge Next Closure Ends (Pretty)"),
        RenfrewBridgeUpcomingClosureCountSensor(coordinator, "Renfrew Bridge Upcoming Closure Count"),
        RenfrewBridgeCurrentClosureEndsSensor(coordinator, "Renfrew Bridge Current Closure Ends"),
        RenfrewBridgeCurrentClosureEndsPrettySensor(coordinator, "Renfrew Bridge Current Closure Ends Pretty")
    ]
    async_add_entities(entities)

class RenfrewBridgeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Renfrew Bridge sensors."""

    def __init__(self, coordinator, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._entry_id = coordinator.config_entry.entry_id
        slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        self._attr_unique_id = f"{self._entry_id}_{slug}"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Renfrew Bridge",
            "manufacturer": "Renfrewshire Council/West Dumbartonshire Council",
            "entry_type": "service"
        }

class RenfrewBridgeStatusSensor(RenfrewBridgeBaseSensor):
    """Sensor for the current bridge status."""
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return "closed" if data['bridge_closed'] else "open"

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:bridge"

class RenfrewBridgeNextClosureStartsPrettySensor(RenfrewBridgeBaseSensor):
    """Sensor for the next closure in a pretty format."""
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data or not data.get("next_closure_start"):
            return None
        try:
            dt = datetime.fromisoformat(data["next_closure_start"])
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return None

class RenfrewBridgeNextClosureEndsPrettySensor(RenfrewBridgeBaseSensor):
    """Sensor for the next closure end in a pretty format."""
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data or not data.get("next_closure_end"):
            return None
        try:
            dt = datetime.fromisoformat(data["next_closure_end"])
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return None

class RenfrewBridgeUpcomingClosureCountSensor(RenfrewBridgeBaseSensor):
    """Sensor for the count of upcoming closures."""
    def __init__(self, coordinator, name):
        super().__init__(coordinator, name)
        self._attr_icon = "mdi:counter"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data or not data.get("closure_times"):
            return 0
        now = datetime.now()
        count = len([c for c in data["closure_times"] if c[0] > now])
        return count

class RenfrewBridgeCurrentClosureEndsSensor(RenfrewBridgeBaseSensor):
    """Sensor for when the current closure ends."""
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data or not data.get("bridge_closed"):
            return None
        return data.get("next_closure_end")

class RenfrewBridgeCurrentClosureEndsPrettySensor(RenfrewBridgeBaseSensor):
    """Sensor for when the current closure ends in a pretty format."""
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data or not data.get("bridge_closed") or not data.get("next_closure_end"):
            return None
        try:
            end_time_str = data["next_closure_end"]
            end_dt = datetime.fromisoformat(end_time_str)
            return end_dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return None