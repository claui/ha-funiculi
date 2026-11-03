"""Tests for the Funiculi entities and options flow."""

# pylint: disable=magic-value-comparison

from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.funiculi.const import CONF_SOURCES, DOMAIN


def make_entry() -> MockConfigEntry:
    """Returns an unregistered config entry for a test amp."""
    return MockConfigEntry(
        domain=DOMAIN,
        title='Funiculi',
        data={
            CONF_HOST: '192.168.0.151',
            CONF_PORT: 23,
            CONF_SOURCES: ['ANALOG1', 'TV'],
        },
    )


@patch('custom_components.funiculi.coordinator.AsyncApi')
async def test_entities_follow_the_coordinator(
    mock_api: AsyncMock, hass: HomeAssistant
) -> None:
    """Switch, number and select mirror the polled amp state."""
    api = mock_api.return_value
    api.status = AsyncMock(return_value='PWSTANDBY')
    api.volume.get = AsyncMock(return_value=18.0)
    api.source.get = AsyncMock(return_value='ANALOG1')
    api.on = AsyncMock()
    api.off = AsyncMock()
    api.volume.set = AsyncMock()
    api.source.set = AsyncMock()
    entry = make_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    power = hass.states.get('switch.funiculi')
    volume = hass.states.get('number.funiculi_volume')
    source = hass.states.get('select.funiculi_source')
    assert power is not None and power.state == 'off'
    assert volume is not None and volume.state == '18.0'
    assert source is not None and source.state == 'ANALOG1'

    await hass.services.async_call(
        'switch',
        'turn_on',
        {'entity_id': 'switch.funiculi'},
        blocking=True,
    )
    api.on.assert_awaited_once()
    await hass.services.async_call(
        'number',
        'set_value',
        {'entity_id': 'number.funiculi_volume', 'value': 30},
        blocking=True,
    )
    api.volume.set.assert_awaited_once_with(30.0)
    await hass.services.async_call(
        'select',
        'select_option',
        {'entity_id': 'select.funiculi_source', 'option': 'TV'},
        blocking=True,
    )
    api.source.set.assert_awaited_once_with('TV')

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    power_after = hass.states.get('switch.funiculi')
    assert power_after is not None
    assert power_after.state == 'unavailable'


@patch('custom_components.funiculi.coordinator.AsyncApi')
async def test_options_flow_updates_sources(
    mock_api: AsyncMock, hass: HomeAssistant
) -> None:
    """Editing the sources reloads the entry with new options."""
    api = mock_api.return_value
    api.status = AsyncMock(return_value='PWON')
    api.volume.get = AsyncMock(return_value=10.0)
    api.source.get = AsyncMock(return_value='TV')
    entry = make_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        entry.entry_id
    )
    result = await hass.config_entries.options.async_configure(
        result['flow_id'], user_input={CONF_SOURCES: 'TV, phono'}
    )
    await hass.async_block_till_done()
    assert entry.options == {CONF_SOURCES: ['TV', 'PHONO']}
    select = hass.states.get('select.funiculi_source')
    assert select is not None
    assert select.attributes['options'] == ['TV', 'PHONO']
