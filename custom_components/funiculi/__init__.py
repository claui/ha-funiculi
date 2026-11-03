"""The Funiculi (Denon AVR Telnet) integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import FuniculiCoordinator

PLATFORMS = [Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

type FuniculiConfigEntry = ConfigEntry[FuniculiCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: FuniculiConfigEntry
) -> bool:
    """Sets up the integration from a config entry.

    :param hass: The running Home Assistant instance.

    :param entry: The config entry to set up.

    :return: whether the setup succeeded.
    """
    coordinator = FuniculiCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(
        entry, PLATFORMS
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: FuniculiConfigEntry
) -> bool:
    """Unloads a config entry.

    :param hass: The running Home Assistant instance.

    :param entry: The config entry to unload.

    :return: whether the unload succeeded.
    """
    return await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )


async def async_reload_entry(
    hass: HomeAssistant, entry: FuniculiConfigEntry
) -> None:
    """Reloads a config entry, e.g. after an options change.

    :param hass: The running Home Assistant instance.

    :param entry: The config entry to reload.
    """
    await hass.config_entries.async_reload(entry.entry_id)
