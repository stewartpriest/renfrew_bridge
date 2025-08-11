import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN
from .options_flow import RenfrewBridgeOptionsFlowHandler

class RenfrewBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Renfrew Bridge config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(title="Renfrew Bridge", data={})
        
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RenfrewBridgeOptionsFlowHandler(config_entry)