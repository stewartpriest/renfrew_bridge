# Renfrew Bridge Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://hacs.xyz/)
[![License](https://img.shields.io/github/license/stewartpriest/renfrew_bridge?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/stewartpriest/renfrew_bridge?style=flat-square)](https://github.com/stewartpriest/renfrew_bridge/stargazers)
[![Forks](https://img.shields.io/github/forks/stewartpriest/renfrew_bridge?style=flat-square)](https://github.com/stewartpriest/renfrew_bridge/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/stewartpriest/renfrew_bridge?style=flat-square)](https://github.com/stewartpriest/renfrew_bridge/commits/main)

![Logo](https://raw.githubusercontent.com/stewartpriest/renfrew_bridge/main/.github/logo.png)

This Home Assistant integration monitors the operational status of the **Renfrew Bridge**, providing real-time data on:

- 🚦 Whether the bridge is currently **open** or **closed**
- 📆 The **next planned closure time**
- 🔢 The **number of upcoming closures**
- 🕒 A user-friendly display of next and current closure end times in **UK date format**

It’s especially useful for residents and commuters near **Braehead, Renfrew, Clydebank and Yoker**, helping avoid delays caused by river traffic bridge openings.

---

## 🧰 Features

| Sensor | Description |
|--------|-------------|
| `sensor.renfrew_bridge_status` | Shows if the bridge is currently `open` or `closed` |
| `sensor.renfrew_bridge_next_closure` | ISO 8601 datetime of the next planned closure |
| `sensor.renfrew_bridge_next_closure_pretty` | Human-friendly format: `DD/MM/YYYY HH:mm` |
| `sensor.renfrew_bridge_upcoming_closure_count` | Integer count of future closures (excluding any ongoing one) |
| `sensor.renfrew_bridge_current_closure_ends` | ISO datetime for when the current closure ends (if bridge is closed) |
| `sensor.renfrew_bridge_current_closure_ends_pretty` | Human-friendly format of closure end time: `DD/MM/YYYY HH:mm` |

---

## 🚀 Installation (via HACS)

1. In Home Assistant, open **HACS → Integrations**
2. Click the three dots (⋮) → **Custom Repositories**
3. Add the repository:
   ```
   https://github.com/stewartpriest/renfrew_bridge
   ```
   - Category: **Integration**

4. Install the **Renfrew Bridge** integration from the list
5. Restart Home Assistant

---

## ⚙️ Configuration

Once installed:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Renfrew Bridge**
4. Set the **Refresh Rate (minutes)** — this controls how often the bridge status is refreshed

You can adjust the refresh rate any time via:
- **Settings → Devices & Services → Renfrew Bridge → Configure**

---

## 🧠 Use Cases

- **Automation**: Alert users when a closure is upcoming or ends
- **Lovelace Dashboards**: Show next and current closures in a readable format
- **Voice Assistants**: "Hey Google, is the bridge open?"
- **Travel Planning**: Display how many bridge closures are scheduled ahead

---

## 📌 Notes

- The integration scrapes [Renfrewshire Council’s bridge closure schedule](https://www.renfrewshire.gov.uk/renfrew-bridge)
- No API key or login required
- Closure times and formats are automatically parsed
- Sensors that show "None" indicate no active or relevant closure

---

## 📦 Attribution

Developed by [@stewartpriest](https://github.com/stewartpriest)  
Bridge status and timing from Renfrewshire Council

---

## 🧾 License

[MIT License](LICENSE)
