# Renfrew Bridge Home Assistant Integration

![Logo](https://raw.githubusercontent.com/stewartpriest/renfrew_bridge/main/.github/logo.png)

This Home Assistant integration monitors the operational status of the **Renfrew Bridge**, providing real-time data on:

- 🚦 Whether the bridge is currently **open** or **closed**
- 📆 The **next planned closure time**
- 🕒 A user-friendly display of the next closure in **UK date format**

It’s especially useful for residents and commuters near **Braehead, Renfrew, Clydebank and Yoker**, helping avoid delays caused by river traffic bridge openings.

---

## 🧰 Features

| Sensor | Description |
|--------|-------------|
| `sensor.renfrew_bridge_status` | Shows if the bridge is currently `open` or `closed` |
| `sensor.renfrew_bridge_next_closure` | ISO 8601 datetime of the next planned closure |
| `sensor.renfrew_bridge_next_closure_pretty` | Human-friendly `DD/MM/YYYY HH:mm` format |

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
4. Set the **Refresh Rate (minutes)** — this controls how often bridge status is refreshed

---

## 🛠️ Options

You can adjust the refresh interval at any time by:

- Going to **Settings → Devices & Services → Renfrew Bridge → Configure**

---

## 🧠 Use Cases

- **Automation**: Alert users when the bridge is about to close
- **Lovelace Cards**: Display the next closure time on a dashboard
- **Voice Assistants**: "Hey Google, is the bridge open?"

---

## 📌 Notes

- The integration scrapes [Renfrewshire Council’s bridge closure schedule](https://www.renfrewshire.gov.uk/renfrew-bridge)
- No API key or login required
- Refresh rate is user-defined

---

## 📦 Attribution

Developed by [@stewartpriest](https://github.com/stewartpriest)  
Bridge status and timing from Renfrewshire Council

---

## 🧾 License

[MIT License](LICENSE)
