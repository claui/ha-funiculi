"""Global fixtures for the integration test suite."""

import pytest

# pytest mandates this exact lowercase name for plugin activation.
pytest_plugins = 'pytest_homeassistant_custom_component'  # pylint: disable=invalid-name


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,  # pylint: disable=unused-argument
) -> None:
    """Lets the test harness load our custom_components folder.

    :param enable_custom_integrations:
        The harness fixture doing the actual work; requested here
        solely to activate it for every test.
    """
