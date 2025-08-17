import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_REFRESH_MINUTES,
    DEFAULT_REFRESH_MINUTES,
)
from .options_flow import RenfrewBridgeOptionsFlowHandler

_LOGGER = logging.getLogger(__name__)

class RenfrewBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renfrew Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)
            return self.async_create_entry(
                title="Renfrew Bridge",
                data={
                    CONF_REFRESH_MINUTES: user_input[CONF_REFRESH_MINUTES]
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_REFRESH_MINUTES,
                    default=DEFAULT_REFRESH_MINUTES
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=60))
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return RenfrewBridgeOptionsFlowHandler(config_entry)
