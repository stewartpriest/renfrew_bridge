import voluptuous as vol
from homeassistant import config_entries
from .const import CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES

class RenfrewBridgeOptionsFlowHandler(config_entries.OptionsFlow):

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="", data={CONF_REFRESH_MINUTES: user_input[CONF_REFRESH_MINUTES]}
            )

        current = self.config_entry.options.get(
            CONF_REFRESH_MINUTES,
            self.config_entry.data.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_MINUTES, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=60)
                )
            })
        )