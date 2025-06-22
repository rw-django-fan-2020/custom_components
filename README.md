# Beat Mode Integration for Home Assistant

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/your-username/beat_mode)
![License](https://img.shields.io/github/license/your-username/beat_mode)

## Overview

`beat_mode` is a Home Assistant custom integration that adds a “Beat Mode” switch to compatible lights.
When enabled, the Beat Mode syncs your lights’ colors to an external beat signal, creating dynamic lighting effects.

---

## Features

- Adds a switch entity to color-capable lights for toggling Beat Mode.
- Supports beat data via HTTP requests or MQTT messages.
- Configurable through the Home Assistant UI using `config_flow`.
- Async and resource-efficient design.
- Proper device and entity association in Home Assistant.

---

## Installation

1. Copy the `beat_mode` folder into your Home Assistant `custom_components` directory:

config/
└── custom_components/
└── beat_mode/
├── init.py
├── switch.py
├── config_flow.py
├── manifest.json
└── ...

2. Restart Home Assistant.

3. Add the integration via the UI: **Settings > Devices & Services > Add Integration > Beat Mode**.

4. Configure connection details (e.g., `host`, `token`) through the UI.

---

## Configuration

The integration uses a `config_flow` for easy setup and does **not** require manual `configuration.yaml` entries.

If you prefer manual configuration, here is an example:

```yaml
beat_mode:
host: "192.168.1.100"
token: "YOUR_API_TOKEN"

## Usage

    After setup, you will see additional switch entities for your compatible lights.

    Toggle the Beat Mode switch to start or stop the dynamic color changes synced to the beat.

    When off, lights behave normally.

---

## Development & Debugging

    Check logs in Home Assistant under Settings > System > Logs.

    Enable debug logging for custom_components.beat_mode for detailed output.

---

## License

MIT License. See the LICENSE file for details.

---

## Contributing

Feel free to open issues or pull requests on the GitHub repository for bugs, features, or improvements.
Contact

For questions or support, reach out via [your email or GitHub link].