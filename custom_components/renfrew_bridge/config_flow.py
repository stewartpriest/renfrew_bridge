import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES

class RenfrewBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Renfrew Bridge config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Renfrew Bridge", 
                data={CONF_REFRESH_MINUTES: user_input[CONF_REFRESH_MINUTES]}
            )

        data_schema = vol.Schema({
            vol.Required(
                CONF_REFRESH_MINUTES,
                default=DEFAULT_REFRESH_MINUTES
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=60))
        })
        
        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors={}
        )