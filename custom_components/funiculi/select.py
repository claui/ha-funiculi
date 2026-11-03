"""The audio source select platform for the Funiculi integration."""

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FuniculiConfigEntry
from .const import CONF_SOURCES
from .coordinator import FuniculiCoordinator
from .entity import FuniculiEntity


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FuniculiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Adds the audio source select for one config entry.

    :param entry: The config entry to set up.

    :param async_add_entities: The callback adding our entities.
    """
    async_add_entities(
        [FuniculiSourceSelect(entry.runtime_data, entry)]
    )


class FuniculiSourceSelect(FuniculiEntity, SelectEntity):
    # pylint: disable=abstract-method
    # SelectEntity bridges its abstract sync selectors to their
    # async counterparts; pylint cannot see that mapping.

    """The amp’s selected audio source.

    :param coordinator: The coordinator polling the amp.

    :param entry:
        The config entry holding the amp’s source names, since
        Denon’s telnet protocol cannot enumerate them.
    """

    _attr_name = 'Source'

    def __init__(
        self,
        coordinator: FuniculiCoordinator,
        entry: FuniculiConfigEntry,
    ) -> None:
        super().__init__(coordinator, 'source')
        self._attr_options = entry.options.get(
            CONF_SOURCES, entry.data.get(CONF_SOURCES, [])
        )

    @property
    def current_option(self) -> str | None:
        """The currently selected source, if it is a known one."""
        if (data := self.coordinator.data) is None:
            return None
        return (
            data.source if data.source in self._attr_options else None
        )

    async def async_select_option(self, option: str) -> None:
        """Selects an audio source.

        :param option: The source name to select.
        """
        await self.coordinator.api.source.set(option)
        await self.coordinator.async_request_refresh()
