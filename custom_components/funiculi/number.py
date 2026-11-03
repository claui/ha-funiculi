"""The master volume number platform for the Funiculi integration."""

from funiculi.async_api import VOLUME_MAX, VOLUME_MIN

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FuniculiConfigEntry
from .coordinator import FuniculiCoordinator
from .entity import FuniculiEntity


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FuniculiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Adds the master volume number for one config entry.

    :param entry: The config entry to set up.

    :param async_add_entities: The callback adding our entities.
    """
    async_add_entities([FuniculiVolumeNumber(entry.runtime_data)])


class FuniculiVolumeNumber(FuniculiEntity, NumberEntity):
    # pylint: disable=abstract-method
    # NumberEntity bridges its abstract sync setters to their async
    # counterparts; pylint cannot see that mapping.

    """The amp’s master volume level, 0–98 in half steps.

    :param coordinator: The coordinator polling the amp.
    """

    _attr_name = 'Volume'
    _attr_native_min_value = VOLUME_MIN
    _attr_native_max_value = VOLUME_MAX
    _attr_native_step = 0.5

    def __init__(self, coordinator: FuniculiCoordinator) -> None:
        super().__init__(coordinator, 'volume')

    @property
    def native_value(self) -> float | None:
        """The current master volume level."""
        if (data := self.coordinator.data) is None:
            return None
        return data.volume

    async def async_set_native_value(self, value: float) -> None:
        """Sets the master volume level.

        :param value: The volume level between 0 and 98.
        """
        await self.coordinator.api.volume.set(value)
        await self.coordinator.async_request_refresh()
