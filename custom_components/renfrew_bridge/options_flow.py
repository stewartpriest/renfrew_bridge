import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES

class RenfrewBridgeOptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        pass

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Required(
                CONF_REFRESH_MINUTES,
                default=self.config_entry.options.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=60))
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)