import logging
from datetime import timedelta
from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES
from .coordinator import RenfrewBridgeDataUpdateCoordinator
from .bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up Renfrew Bridge from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    if CONF_REFRESH_MINUTES in entry.options:
        refresh_minutes = entry.options.get(CONF_REFRESH_MINUTES)
    else:
        refresh_minutes = entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)

    _LOGGER.info("Configured refresh_minutes is: %s", refresh_minutes)
    
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
    
    # Register a manual update service
    async def async_manual_update_service(call):
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "manual_update", async_manual_update_service)
   
    # Set up the platforms (sensors and binary sensors)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    
    # Listen for changes to options and reload the component if they change
    entry.async_on_unload(entry.add_update_listener(async_reload))
    
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_reload(hass, entry):
    """Reload the component when the options change."""
    await hass.config_entries.async_reload(entry.entry_id)