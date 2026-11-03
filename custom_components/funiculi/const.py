"""Constants for the Funiculi integration."""

DOMAIN = 'funiculi'

CONF_SOURCES = 'sources'

POWER_ON = 'PWON'

DEFAULT_CTRL_PORT = 23
# Verified settable via SI on a PMA-900HNE (Aios 6.0V, fw 2.47.350):
# the display shows ANALOG1 as "AUX"; other plausible names (PHONO,
# SOURCE, COAX, MPLAY, BLUETOOTH, AUX, …) are silently rejected.
DEFAULT_SOURCES = (
    'ANALOG1',
    'OPTICAL1',
    'OPTICAL2',
    'OPTICAL3',
    'COAXIAL',
    'BT',
)
COMMAND_TIMEOUT_MS = 1000
UPDATE_INTERVAL_S = 5
