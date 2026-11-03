"""The power switch platform for the Funiculi integration."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FuniculiConfigEntry
from .const import POWER_ON
from .coordinator import FuniculiCoordinator
from .entity import FuniculiEntity


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FuniculiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Adds the power switch for one config entry.

    :param entry: The config entry to set up.

    :param async_add_entities: The callback adding our entities.
    """
    async_add_entities([FuniculiPowerSwitch(entry.runtime_data)])


class FuniculiPowerSwitch(FuniculiEntity, SwitchEntity):
    # pylint: disable=abstract-method
    # SwitchEntity bridges ToggleEntity’s abstract sync methods to
    # their async counterparts; pylint cannot see that mapping.

    """The amp’s power state, on and standby.

    :param coordinator: The coordinator polling the amp.
    """

    _attr_name = None

    def __init__(self, coordinator: FuniculiCoordinator) -> None:
        super().__init__(coordinator, 'power')

    @property
    def is_on(self) -> bool | None:
        """Whether the amp is on rather than on standby."""
        if (data := self.coordinator.data) is None:
            return None
        return data.power == POWER_ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turns the amp on.

        :param kwargs: Ignored switch service parameters.
        """
        await self.coordinator.api.on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turns the amp to standby.

        :param kwargs: Ignored switch service parameters.
        """
        await self.coordinator.api.off()
        await self.coordinator.async_request_refresh()
