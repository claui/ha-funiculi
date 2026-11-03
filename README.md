# Funiculi (Denon AVR Telnet)

A Home Assistant integration for Denon AVR amplifiers that exposes the
features only Denon’s telnet control protocol provides — above all
**power on/standby**, which neither the HEOS nor the DLNA/UPnP
interfaces of these amps can do.

It is the Home Assistant counterpart of the
[funiculi](https://github.com/claui/funiculi) command line tool and
builds on the same protocol library.

## Why this exists

HEOS-based Denon amps such as the PMA-900HNE expose three network
interfaces: HEOS (playback, no power), DLNA/UPnP (streaming, no
power), and the legacy telnet control protocol (power, volume,
source). The built-in `denonavr` integration needs the amps’ HTTP
API, which HEOS-class firmware answers with `403 Forbidden` on every
path — so power control is only reachable over telnet. This
integration fills exactly that gap; it is deliberately complementary
to the `heos` and `dlna_dmr` integrations rather than a replacement.

## Entities

For each configured amplifier (device name taken from the config
entry title):

| Entity | Type | Purpose |
| --- | --- | --- |
| `<device>` | `switch` | Power on / standby (`PWON` / `PWSTANDBY`) |
| `<device> Volume` | `number` | Master volume, 0–98 in half steps |
| `<device> Source` | `select` | Audio source selection (`SI` commands) |

The source list is a config option: Denon’s telnet protocol cannot
enumerate a model’s sources, so the flow asks for them (comma-
separated, e.g. `ANALOG1, TV, PHONO, MPLAY`). Check
`funiculi source get` while the amp is set to a known source to find
the names your model uses.

## Installation

### HACS / Marketplace

Add this repository to HACS as a custom repository (category
*Integration*), or install it from the Marketplace once it is listed
there. The integration pulls its protocol library (`funiculi`) from
PyPI as a manifest requirement.

### Manual

Copy `custom_components/funiculi/` into your Home Assistant
configuration directory’s `custom_components/`, restart, then add
*Funiculi (Denon AVR Telnet)* under **Settings → Devices & services**.

## Configuration

The config flow asks for:

- **Host** — the amp’s address, e.g. `192.168.0.151`
- **Control port** — the telnet control port, default `23`
- **Source names** — comma-separated, see above

Source names can be changed later via the entry’s options.

## Development

The repository is a uv virtual project (no Python package of its
own); the protocol library is consumed from a sibling checkout:

```shell
uv sync
uv run poe tests       # pytest with the Home Assistant test harness
uv run poe typecheck   # mypy
uv run poe linter      # pylint
uv run poe formatcheck # ruff format --check
```

## License

Copyright (c) 2026 Claudia Pellegrino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
For a copy of the License, see [LICENSE](LICENSE).
