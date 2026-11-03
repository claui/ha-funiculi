"""The data update coordinator for the Funiculi integration."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from funiculi import AsyncApi
from funiculi.errors import FuniculiError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COMMAND_TIMEOUT_MS,
    DEFAULT_CTRL_PORT,
    DOMAIN,
    UPDATE_INTERVAL_S,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class FuniculiState:
    """The polled state of one Denon AVR.

    :param power:
        `PWON` if the amp is on, `PWSTANDBY` if it is on standby,
        or `None` if it did not answer.

    :param volume: The master volume level between 0 and 98.

    :param source: The name of the selected audio source.
    """

    power: str | None
    volume: float | None
    source: str | None


class FuniculiCoordinator(DataUpdateCoordinator[FuniculiState]):
    """Polls power, volume and source over Denon’s telnet protocol."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_S),
        )
        self.api = AsyncApi(
            host=entry.data[CONF_HOST],
            ctrlport=entry.data.get(CONF_PORT, DEFAULT_CTRL_PORT),
            timeout=COMMAND_TIMEOUT_MS,
        )

    async def _async_update_data(self) -> FuniculiState:
        try:
            return await self._poll()
        except FuniculiError as error:
            raise UpdateFailed(
                f'Cannot reach the AVR: {error}'
            ) from error

    async def _poll(self) -> FuniculiState:
        power = await self.api.status()
        volume = await self.api.volume.get()
        source = await self.api.source.get()
        return FuniculiState(power or None, volume, source or None)
