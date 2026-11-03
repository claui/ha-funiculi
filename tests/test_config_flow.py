"""Tests for the Funiculi config flow."""

# pylint: disable=magic-value-comparison

from unittest.mock import AsyncMock, patch

from funiculi.errors import ConnectionFailed
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.funiculi.const import CONF_SOURCES, DOMAIN

USER_INPUT = {
    CONF_HOST: '192.168.0.151',
    CONF_PORT: 23,
    CONF_SOURCES: 'ANALOG1, tv',
}


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """A reachable amp yields a config entry with parsed sources."""
    with patch(
        'custom_components.funiculi.config_flow.AsyncApi'
    ) as mock_api:
        mock_api.return_value.status = AsyncMock(
            return_value='PWSTANDBY'
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={'source': config_entries.SOURCE_USER}
        )
        assert result['type'] is FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            result['flow_id'], user_input=USER_INPUT
        )
    assert result['type'] is FlowResultType.CREATE_ENTRY
    assert result['title'] == '192.168.0.151'
    assert result['data'] == {
        CONF_HOST: '192.168.0.151',
        CONF_PORT: 23,
        CONF_SOURCES: ['ANALOG1', 'TV'],
    }


async def test_user_flow_rejects_silence(hass: HomeAssistant) -> None:
    """An amp that never answers shows the connection error."""
    with patch(
        'custom_components.funiculi.config_flow.AsyncApi'
    ) as mock_api:
        mock_api.return_value.status = AsyncMock(return_value='')
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={'source': config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result['flow_id'], user_input=USER_INPUT
        )
        assert result['type'] is FlowResultType.FORM
        assert result['errors'] == {'base': 'cannot_connect'}


async def test_user_flow_rejects_unreachable(
    hass: HomeAssistant,
) -> None:
    """A connection failure shows the connection error."""
    with patch(
        'custom_components.funiculi.config_flow.AsyncApi'
    ) as mock_api:
        mock_api.return_value.status = AsyncMock(
            side_effect=ConnectionFailed('nope')
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={'source': config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result['flow_id'], user_input=USER_INPUT
        )
        assert result['type'] is FlowResultType.FORM
        assert result['errors'] == {'base': 'cannot_connect'}
