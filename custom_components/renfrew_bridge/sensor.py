import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES
from custom_components.renfrew_bridge.bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.info("Renfrew Bridge: async_setup_entry called")

    refresh_minutes = config_entry.options.get(CONF_REFRESH_MINUTES) or config_entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
    entry_id = config_entry.entry_id

    entities = [
        RenfrewBridgeStatusSensor("Renfrew Bridge Status", refresh_minutes, entry_id),
        RenfrewBridgeNextClosurePrettySensor("Renfrew Bridge Next Closure (Pretty)", refresh_minutes, entry_id),
        RenfrewBridgeUpcomingClosureCountSensor("Renfrew Bridge Upcoming Closure Count", refresh_minutes, entry_id),
        RenfrewBridgeCurrentClosureEndsSensor("Renfrew Bridge Current Closure Ends", refresh_minutes, entry_id),
        RenfrewBridgeCurrentClosureEndsPrettySensor("Renfrew Bridge Current Closure Ends Pretty", refresh_minutes, entry_id)
    ]

    async_add_entities(entities)


class TimedUpdateSensor(SensorEntity):
    def __init__(self, name, refresh_minutes, entry_id):
        self._attr_name = name
        self._attr_native_value = None
        self._refresh = timedelta(minutes=refresh_minutes)
        self._last_update = datetime.min
        self._entry_id = entry_id
        slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
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


class RenfrewBridgeStatusSensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Bridge status sensor received: %s", status)
            self._attr_native_value = "closed" if status['bridge_closed'] else "open"
            self._last_update = datetime.now()
            self._attr_icon = "mdi:bridge"
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge status: %s", e)
            self._attr_native_value = None


        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Binary bridge status sensor received: %s", status)
            self._attr_is_on = status["bridge_closed"]
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update binary bridge status: %s", e)
            self._attr_is_on = None


class RenfrewBridgeNextClosureSensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            value = status.get("next_closure_start")
            if value is None:
                _LOGGER.warning("Next closure sensor: No upcoming closures detected (next_closure_start is None)")
            else:
                _LOGGER.info("Next closure sensor: next_closure_start = %s", value)
            self._attr_native_value = value
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
            raw = status.get("next_closure_start")
            if raw is None:
                _LOGGER.warning("Pretty closure sensor: next_closure_start is None (no upcoming closures?)")
                self._attr_native_value = "None"
            else:
                dt = datetime.fromisoformat(raw)
                pretty = dt.strftime("%d/%m/%Y %H:%M")
                _LOGGER.info("Pretty closure sensor: formatted %s to '%s'", raw, pretty)
                self._attr_native_value = pretty
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to format Renfrew Bridge next closure pretty: %s", e)
            self._attr_native_value = None


class RenfrewBridgeUpcomingClosureCountSensor(TimedUpdateSensor):
    def _default_icon(self):
        return "mdi:counter"

    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Upcoming closure count sensor received: %s", status)
            closure_times = status.get("closure_times", [])
            count = len([c for c in closure_times if c[0] > datetime.now()])
            self._attr_native_value = count
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update Renfrew Bridge upcoming closure count: %s", e)
            self._attr_native_value = None


class RenfrewBridgeCurrentClosureEndsSensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Current closure end sensor received: %s", status)
            if status.get("bridge_closed") and status.get("next_closure_start") and status.get("next_closure_end"):
                now = datetime.now()
                start = datetime.fromisoformat(status["next_closure_start"])
                end = datetime.fromisoformat(status["next_closure_end"])
                if start <= now <= end:
                    self._attr_native_value = status["next_closure_end"]
                else:
                    self._attr_native_value = None
            else:
                self._attr_native_value = None
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update current closure ends sensor: %s", e)
            self._attr_native_value = None


class RenfrewBridgeCurrentClosureEndsPrettySensor(TimedUpdateSensor):
    def update(self):
        if not self.should_update():
            return
        try:
            status = get_bridge_status()
            _LOGGER.info("Current closure end (pretty) sensor received: %s", status)
            if status.get("bridge_closed") and status.get("next_closure_start") and status.get("next_closure_end"):
                now = datetime.now()
                start = datetime.fromisoformat(status["next_closure_start"])
                end = datetime.fromisoformat(status["next_closure_end"])
                if start <= now <= end:
                    self._attr_native_value = end.strftime("%d/%m/%Y %H:%M")
                else:
                    self._attr_native_value = None
            else:
                self._attr_native_value = None
            self._last_update = datetime.now()
        except Exception as e:
            _LOGGER.error("Failed to update current closure ends pretty sensor: %s", e)
            self._attr_native_value = None
