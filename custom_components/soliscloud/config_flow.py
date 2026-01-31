import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from .const import DOMAIN
from .solis_api import SolisClient

_LOGGER = logging.getLogger(__name__)

CONF_API_ID = "api_id"
CONF_API_SECRET = "api_secret"


class SolisCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SolisCloud."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_id = user_input[CONF_API_ID]
            api_secret = user_input[CONF_API_SECRET]

            # Test the connection
            client = SolisClient(api_id, api_secret)
            try:
                result = await self.hass.async_add_executor_job(
                    client.inverter_list, 1, 1
                )
                if result.get("success") is False:
                    errors["base"] = "invalid_auth"
                else:
                    await self.async_set_unique_id(api_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="SolisCloud",
                        data={
                            CONF_API_ID: api_id,
                            CONF_API_SECRET: api_secret,
                        },
                    )
            except Exception:
                _LOGGER.exception("Error connecting to SolisCloud API")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_ID): str,
                    vol.Required(CONF_API_SECRET): str,
                }
            ),
            errors=errors,
        )
