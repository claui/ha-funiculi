"""The common base entity for the Funiculi integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FuniculiCoordinator


class FuniculiEntity(CoordinatorEntity[FuniculiCoordinator]):
    """Shares device info and unique ID scheme across all entities.

    :param coordinator: The coordinator polling the amp.

    :param suffix:
        A per-platform suffix keeping unique IDs distinct within
        one config entry.
    """

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: FuniculiCoordinator, suffix: str
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f'{coordinator.config_entry.entry_id}_{suffix}'
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer='Denon',
            name=coordinator.config_entry.title,
        )
