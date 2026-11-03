"""The config flow for the Funiculi integration."""

import re
from typing import Any

import aiohttp
from funiculi import AsyncApi
from funiculi.errors import FuniculiError
from funiculi.settings import DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv

from . import FuniculiConfigEntry
from .const import (
    COMMAND_TIMEOUT_MS,
    CONF_SOURCES,
    DEFAULT_CTRL_PORT,
    DEFAULT_SOURCES,
    DOMAIN,
)

_FRIENDLY_NAME = re.compile(
    r'<friendlyName>(?P<name>[^<]+)</friendlyName>'
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
                    title=await _async_fetch_title(self.hass, host),
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


async def _async_fetch_title(hass: HomeAssistant, host: str) -> str:
    """Queries the amp’s UPnP description for a human-readable name.

    :param hass: The running Home Assistant instance.

    :param host: The AVR host to query.

    :return:
        The device’s friendly name, or `host` itself if the
        description cannot be fetched or parsed.
    """
    session = async_get_clientsession(hass)
    try:
        text = await _async_fetch_description(session, host)
    except aiohttp.ClientError, TimeoutError:
        return host
    match = _FRIENDLY_NAME.search(text)
    return match.group('name').strip() if match else host


async def _async_fetch_description(
    session: aiohttp.ClientSession, host: str
) -> str:
    """Fetches the UPnP device description of an amp.

    :param session: The HTTP session to query with.

    :param host: The AVR host to query.

    :return: The device description XML, as text.

    :raises aiohttp.ClientError: if the request fails.

    :raises TimeoutError: if the amp does not answer in time.
    """
    response = await session.get(
        f'http://{host}:60006{DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH}',
        timeout=aiohttp.ClientTimeout(total=5),
    )
    return await response.text()
