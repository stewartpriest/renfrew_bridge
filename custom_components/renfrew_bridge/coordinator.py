from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
from .const import DOMAIN, DEFAULT_REFRESH_MINUTES
from .bridge_status import get_bridge_status

_LOGGER = logging.getLogger(__name__)

class RenfrewBridgeDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching Renfrew Bridge data."""

    def __init__(self, hass, refresh_minutes):
        """Initialize the coordinator."""
        self.bridge_status = {}
        update_interval = timedelta(minutes=refresh_minutes) if refresh_minutes > 0 else None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from the Renfrew Bridge website."""
        try:
            data = await self.hass.async_add_executor_job(get_bridge_status)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err