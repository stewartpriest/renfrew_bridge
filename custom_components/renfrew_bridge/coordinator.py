from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
from .const import DOMAIN
from .bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

class RenfrewBridgeDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, refresh_minutes):
        self.bridge_status = {}
        self._refresh_minutes = refresh_minutes
        update_interval = timedelta(minutes=refresh_minutes) if refresh_minutes > 0 else None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def async_start(self):
        """Start polling only if refresh is enabled."""
        if self._refresh_minutes > 0:
            await super().async_start()
        else:
            _LOGGER.info("Polling disabled—coordinator will only update manually.")

    async def _async_update_data(self):
        """Fetch data from the bridge."""
        try:
            data = await self.hass.async_add_executor_job(get_bridge_status)
            _LOGGER.debug("Renfrew Bridge data successfully fetched")
            return data
        except Exception as err:
            _LOGGER.error("Error fetching Renfrew Bridge data: %s", err)
            raise UpdateFailed(f"Error fetching Renfrew Bridge data: {err}") from err
