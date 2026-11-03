"""The config flow for the Funiculi integration."""

from typing import Any

from funiculi import AsyncApi
from funiculi.errors import FuniculiError
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import config_validation as cv

from . import FuniculiConfigEntry
from .const import (
    COMMAND_TIMEOUT_MS,
    CONF_SOURCES,
    DEFAULT_CTRL_PORT,
    DEFAULT_SOURCES,
    DOMAIN,
)

_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_CTRL_PORT): cv.port,
        vol.Required(
            CONF_SOURCES, default=', '.join(DEFAULT_SOURCES)
        ): str,
    }
)


def parse_sources(raw: str) -> list[str]:
    """Parses a comma-separated source list.

    :param raw: The raw user input, e.g. `ANALOG1, TV`.

    :return:
        The trimmed, uppercased source names, per Denon’s protocol.
    """
    return [
        part.strip().upper() for part in raw.split(',') if part.strip()
    ]


class FuniculiConfigFlow(ConfigFlow, domain=DOMAIN):
    # pylint: disable=abstract-method
    # is_matching is an optional discovery hook; pylint misreads it as
    # an abstract requirement.

    """Collects the amp’s address and its source names."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handles the initial setup dialog.

        :param user_input: The submitted form data, if any.

        :return: The next flow step or the created config entry.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(f'{host}:{port}')
            self._abort_if_unique_id_configured()
            if (error := await _test_connection(host, port)) is None:
                return self.async_create_entry(
                    title=host,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SOURCES: parse_sources(
                            user_input[CONF_SOURCES]
                        ),
                    },
                )
            errors['base'] = error
        return self.async_show_form(
            step_id='user', data_schema=_USER_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: FuniculiConfigEntry,
    ) -> FuniculiOptionsFlow:
        """Returns the options flow for an existing config entry.

        :param config_entry: The entry whose options to edit.

        :return: The options flow handler.
        """
        return FuniculiOptionsFlow()


class FuniculiOptionsFlow(OptionsFlow):
    """Lets users edit the amp’s source names later on."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Shows and processes the options form.

        :param user_input: The submitted form data, if any.

        :return: The next flow step or the stored options.
        """
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_SOURCES: parse_sources(
                        user_input[CONF_SOURCES]
                    )
                }
            )
        current = self.config_entry.options.get(
            CONF_SOURCES, self.config_entry.data.get(CONF_SOURCES, [])
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCES, default=', '.join(current)
                ): str
            }
        )
        return self.async_show_form(step_id='init', data_schema=schema)


async def _test_connection(host: str, port: int) -> str | None:
    """Probes the amp with a power status query.

    :param host: The AVR host to connect to.

    :param port: The AVR control port to connect to.

    :return: An error key, or `None` if the amp answered.
    """
    api = AsyncApi(host=host, ctrlport=port, timeout=COMMAND_TIMEOUT_MS)
    try:
        status = await api.status()
    except FuniculiError:
        return 'cannot_connect'
    return None if status else 'cannot_connect'
