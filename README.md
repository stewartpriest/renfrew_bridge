# Renfrew Bridge Status (Home Assistant Integration)

Monitors the status of Renfrew Bridge via Renfrewshire Council’s website.

## Features
- Sensor for bridge status (`open`/`closed`)
- Sensor for next scheduled closure

## Installation (HACS)
1. Add this repo as a custom repository in HACS (type: integration)
2. Install **Renfrew Bridge Status**
3. Add the sensor to your `configuration.yaml`:

```yaml
sensor:
  - platform: renfrew_bridge
```

4. Restart Home Assistant.
