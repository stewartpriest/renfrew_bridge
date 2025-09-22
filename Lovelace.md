# 🧭 Renfrew Bridge Status Display

This lovelace example uses Home Assistant sensors and a Jinja-powered Markdown card to display real-time status updates for the Renfrew Bridge. Messages are dynamically rendered based on current and upcoming closures.

---

## 🧾 Example Output Messages

```text
✅ Bridge is currently closed — reopening later  
The Renfrew bridge is currently closed until 21:20.

⏳ Bridge is closed — reopening soon (within 10 minutes)  
The Renfrew bridge is currently closed, scheduled to open in 7 minutes at 21:20.

🕰️ Bridge is closed — reopening imminently  
The Renfrew bridge is currently closed, but is scheduled to reopen imminently at 21:20.

🚧 Upcoming closure — within 30 minutes  
Just a heads up: the Renfrew bridge will close at 21:15 and reopen at 22:00. That’s in 4 minutes.

📅 Upcoming closure — more than 30 minutes away  
The bridge is to close at 21:15 for 45 minutes, opening up again at 22:00.

🛑 Closure just began (within 2-minute grace period)  
The bridge closure has just begun — it’s now in effect and will remain closed until 21:20.

✅ Bridge is open — no upcoming closures  
The bridge is open. There are currently no upcoming closures.
```

# 🧩 Lovelace Card Configuration Example
This example shows how to display the bridge status using a vertical-stack card with [bubble-card](https://github.com/Clooos/Bubble-Card) and a templated markdown card.

<img width="392" height="74" alt="image" src="https://github.com/user-attachments/assets/2562a0c0-1fce-49ac-8e15-7b350fb381c0" />


```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: mdi:bridge
    name: Renfrew Bridge
    modules:
      - default
  - type: markdown
    content: >-
      {# -- Sensor values -- #}

      {%- set status = states('sensor.renfrew_bridge_status') -%}

      {%- set closure_end = states('sensor.renfrew_bridge_current_closure_ends')
      | as_datetime(default = none) -%}

      {%- set count = states('sensor.renfrew_bridge_upcoming_closure_count') |
      int -%}

      {%- set closures =
      state_attr('sensor.renfrew_bridge_upcoming_closure_count',
      'upcoming_closures') -%}

      {%- set now_dt = now() | as_datetime(default = none) -%}


      {# -- Normalize timezone info -- #}

      {%- if closure_end and closure_end.tzinfo is none and now_dt.tzinfo -%}
        {%- set closure_end = closure_end.replace(tzinfo=now_dt.tzinfo) -%}
      {%- endif -%}


      {# -- Active closure with countdown to reopening -- #}

      {%- if status == 'closed' and closure_end -%}
        {%- set minutes_to_open = ((closure_end - now_dt).total_seconds() // 60) | int -%}

        {%- if minutes_to_open > 10 -%}
          The Renfrew bridge is currently closed until {{ closure_end.strftime('%H:%M') }}.
        {%- elif minutes_to_open > 0 -%}
          The Renfrew bridge is currently closed, scheduled to open in {{ minutes_to_open }} minute{{ "s" if minutes_to_open != 1 else "" }} at {{ closure_end.strftime('%H:%M') }}.
        {%- else -%}
          The Renfrew bridge is currently closed, but is scheduled to reopen imminently at {{ closure_end.strftime('%H:%M') }} — assuming no one's lost the keys again.
        {%- endif -%}

      {# -- Upcoming closure with refined phrasing -- #}

      {%- elif count > 0 and closures and closures | length > 0 -%}
        {%- set next = closures[0] -%}
        {%- set start_dt = next.start | as_datetime(default = none) -%}
        {%- set end_dt = next.end | as_datetime(default = none) -%}

        {%- if start_dt and end_dt -%}
          {%- if start_dt.tzinfo is none -%}
            {%- set start_dt = start_dt.replace(tzinfo=now_dt.tzinfo) -%}
          {%- endif -%}
          {%- if end_dt.tzinfo is none -%}
            {%- set end_dt = end_dt.replace(tzinfo=now_dt.tzinfo) -%}
          {%- endif -%}
          {%- if now_dt.tzinfo is none -%}
            {%- set now_dt = now_dt.replace(tzinfo=start_dt.tzinfo) -%}
          {%- endif -%}

          {%- set grace_period = 2 * 60 -%}

          {%- if start_dt > now_dt -%}
            {%- set duration_minutes = ((end_dt - start_dt).total_seconds() // 60) | int -%}
            {%- set time_until_start = ((start_dt - now_dt).total_seconds() // 60) | int -%}

            {%- if time_until_start <= 30 -%}
              Just a heads up: the Renfrew bridge will close at {{ start_dt.strftime('%H:%M') }} and reopen at {{ end_dt.strftime('%H:%M') }}. That’s in {{ time_until_start }} minute{{ "s" if time_until_start != 1 else "" }}.
            {%- else -%}
              The bridge is to close at {{ start_dt.strftime('%H:%M') }} for {{ duration_minutes }} minute{{ "s" if duration_minutes != 1 else "" }}, opening up again at {{ end_dt.strftime('%H:%M') }}.
            {%- endif -%}

          {%- elif start_dt <= now_dt <= end_dt and (now_dt - start_dt).total_seconds() <= grace_period -%}
            The bridge closure has just begun — it’s now in effect and will remain closed until {{ end_dt.strftime('%H:%M') }}.
          {%- endif -%}
        {%- endif -%}

      {# -- Default open message -- #}

      {%- else -%}
        The bridge is open. There are currently no upcoming closures.
      {%- endif -%}

      {{ "\n&nbsp;" }}
    text_only: true

```
