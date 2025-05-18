import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES
from custom_components.renfrew_bridge.bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.info("Renfrew Bridge: async_setup_entry called")

    refresh_minutes = config_entry.options.get(CONF_REFRESH_MINUTES) or config_entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)

    entry_id = config_entry.entry_id

    entities = [
        RenfrewBridgeStatusSensor("Renfrew Bridge Status", refresh_minutes, entry_id),
        RenfrewBridgeNextClosureSensor("Renfrew Bridge Next Closure", refresh_minutes, entry_id),
        RenfrewBridgeNextClosurePrettySensor("Renfrew Bridge Next Closure (Pretty)", refresh_minutes, entry_id)
    ]

    async_add_entities(entities)


class TimedUpdateSensor(SensorEntity):
    def __init__(self, name, refresh_minutes, entry_id):
        self._attr_name = name
        self._attr_native_value = None
        self._refresh = timedelta(minutes=refresh_minutes)
        self._last_update = datetime.min
        self._entry_id = entry_id
        slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{slug}"
        self._attr_icon = self._default_icon()

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

    def _default_icon(self):
        return "mdi:calendar-clock"


class RenfrewBridgeStatusSensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Bridge status sensor received: %s", status)
            self._attr_native_value = "closed" if status['bridge_closed'] else "open"
            self._last_update = datetime.now()
            self._attr_icon = "mdi:bridge" if not status['bridge_closed'] else "mdi:bridge"
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge status: %s", e)
            self._attr_native_value = None


class RenfrewBridgeNextClosureSensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Next closure sensor received: %s", status)
            self._attr_native_value = status['next_closure_start']
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge next closure: %s", e)
            self._attr_native_value = None


class RenfrewBridgeNextClosurePrettySensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Pretty closure sensor received: %s", status)
            raw = status['next_closure_start']
            if raw:
                dt = datetime.fromisoformat(raw)
                self._attr_native_value = dt.strftime("%d/%m/%Y %H:%M")
            else:
                self._attr_native_value = "None"
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to format Renfrew Bridge next closure pretty: %s", e)
            self._attr_native_value = None
