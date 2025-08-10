import logging
from datetime import timedelta
from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES
from .coordinator import RenfrewBridgeDataUpdateCoordinator
from .bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up Renfrew Bridge from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    refresh_minutes = entry.options.get(CONF_REFRESH_MINUTES) or entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
    
    # Perform a single, initial data fetch
    _LOGGER.info("Performing initial data fetch for Renfrew Bridge")
    initial_data = await hass.async_add_executor_job(get_bridge_status)
    
    # Create the coordinator
    coordinator = RenfrewBridgeDataUpdateCoordinator(hass, refresh_minutes)
    
    # Set the coordinator's initial data
    coordinator.data = initial_data

    if refresh_minutes > 0:
        await coordinator.async_config_entry_first_refresh()
    else:
        _LOGGER.info("Renfrew Bridge refresh is disabled (refresh rate = 0)")
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up the platforms (sensors and binary sensors)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok