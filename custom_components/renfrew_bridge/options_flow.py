from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlowWithConfigEntry
import voluptuous as vol

from .const import (
    CONF_REFRESH_MINUTES,
    DEFAULT_REFRESH_MINUTES,
)

class RenfrewBridgeOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle Renfrew Bridge options."""

    def __init__(self, config_entry):
        super().__init__(config_entry)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        refresh = options.get(CONF_REFRESH_MINUTES, self.config_entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES))

        options_schema = vol.Schema({
            vol.Required(CONF_REFRESH_MINUTES, default=refresh): vol.All(vol.Coerce(int), vol.Range(min=0, max=60))
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )
