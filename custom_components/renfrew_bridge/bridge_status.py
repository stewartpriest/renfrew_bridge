from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

def get_bridge_status():
    _LOGGER.info("Renfrew Bridge: get_bridge_status called")

    url = 'https://www.renfrewshire.gov.uk/renfrew-bridge'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    newsflash_div = soup.find('div', class_='newsflash__padding')
    planned_closures = True
    closure_times = []
    last_updated_datetime = None
    next_closure = None
    bridge_closed = False
    current_explicit_date = None

    if newsflash_div:
        paragraphs = newsflash_div.find_all(['p', 'li', 'div'])
        for p in paragraphs:
            text = p.get_text(separator=" ", strip=True)
            text = text.replace("\xa0", " ").replace("  ", " ").strip()
            text = text.replace("a.m.", "am").replace("p.m.", "pm").replace(".", ":").lower()
            text = re.sub(r'(\d{1,2})\.(\d{2})(am|pm)', r'\1:\2\3', text)
            _LOGGER.debug("Raw line: '%s'", text)

            lowered = text.lower()

            if re.search(r'no\s+(further\s+)?closures?\s+(scheduled|planned|expected|currently planned)', lowered) or \
               'no closures currently planned' in lowered or \
               'no road closures planned' in lowered:
                planned_closures = False
                _LOGGER.info("Detected phrasing indicating no planned closures: '%s'", text)

            elif re.search(r'any further closures.*(added|announced|published)', lowered):
                planned_closures = True
                _LOGGER.info("Detected phrasing suggesting future closures may still occur: '%s'", text)

            elif "last updated" in lowered:
                match = re.search(r'last updated\s*[-\u2013]?\s*(.+)', text, flags=re.I)
                if match:
                    cleaned = match.group(1).strip()
                    cleaned = re.sub(r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s*', '', cleaned)
                    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', cleaned)
                    cleaned = re.sub(r'[^\w\s:apm]', '', cleaned, flags=re.I)
                    cleaned = cleaned.replace(" at ", " ")
                    try:
                        last_updated_datetime = datetime.strptime(cleaned, "%d %B %Y %I:%M%p")
                        _LOGGER.debug("Parsed last updated: %s", last_updated_datetime)
                    except ValueError as e:
                        _LOGGER.warning("Failed to parse last updated line: %s", e)

            date_match = re.search(
                r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s*([a-zA-Z]+)\s+(\d{1,2})(st|nd|rd|th)?\s+(\d{4})',
                text.strip().rstrip(":")
            )
            if date_match:
                if 'no closures' in lowered or 'no closure' in lowered:
                    _LOGGER.debug("Skipping date with 'no closures': %s", text)
                    continue
                try:
                    month = date_match.group(2)
                    day = int(date_match.group(3))
                    year = int(date_match.group(5))
                    current_explicit_date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
                    _LOGGER.debug("Set current_explicit_date to: %s", current_explicit_date)
                except ValueError as e:
                    _LOGGER.warning("Failed to parse date: %s", e)

            match1 = re.search(
                r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)?(\d{1,2})(st|nd|rd|th)?\s+([a-zA-Z]+)\s*[-–]?\s*(\d{1,2}:\d{2}\s*[ap]m)\s*(?:until|to)\s*(\d{1,2}:\d{2}\s*[ap]m)',
                text
            )
            if match1:
                try:
                    day = int(match1.group(2))
                    month = match1.group(4)
                    start_time_str = match1.group(5)
                    end_time_str = match1.group(6)
                    year = datetime.now().year
                    start_dt = datetime.strptime(f"{day} {month} {year} {start_time_str}", "%d %B %Y %I:%M%p")
                    end_dt = datetime.strptime(f"{day} {month} {year} {end_time_str}", "%d %B %Y %I:%M%p")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    closure_times.append((start_dt, end_dt))
                    _LOGGER.info("Parsed Format 1 closure: %s to %s", start_dt, end_dt)
                    continue
                except ValueError as e:
                    _LOGGER.error("Error parsing format 1 closure time: %s", e)

            # Format 5 – "friday 20 june from 8:20am to 9:30am"
            match5 = re.search(
                r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(\d{1,2})\s+([a-zA-Z]+)\s+(?:from\s*)?(\d{1,2}:\d{2}\s*[ap]m)\s*(?:until|to)\s*(\d{1,2}:\d{2}\s*[ap]m)',
                text
            )
            if match5:
                try:
                    day = int(match5.group(2))
                    month = match5.group(3)
                    start_str = match5.group(4)
                    end_str = match5.group(5)
                    year = datetime.now().year
                    start_dt = datetime.strptime(f"{day} {month} {year} {start_str}", "%d %B %Y %I:%M%p")
                    end_dt = datetime.strptime(f"{day} {month} {year} {end_str}", "%d %B %Y %I:%M%p")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    closure_times.append((start_dt, end_dt))
                    _LOGGER.info("Parsed Format 5 closure: %s to %s", start_dt, end_dt)
                    continue
                except ValueError as e:
                    _LOGGER.error("Error parsing format 5 closure time: %s", e)

            match3 = re.search(r'(?:from\s*)?(\d{1,2}:\d{2}\s*[ap]m)\s*(?:until|to)\s*(\d{1,2}:\d{2}\s*[ap]m)', text, re.I)
            if match3:
                try:
                    if not current_explicit_date:
                        _LOGGER.debug("Skipping Format 3 - no current_explicit_date set.")
                        continue
                    start_str = match3.group(1).lower()
                    end_str = match3.group(2).lower()
                    date_str = current_explicit_date.strftime("%d %B %Y")
                    start_dt = datetime.strptime(f"{date_str} {start_str}", "%d %B %Y %I:%M%p")
                    end_dt = datetime.strptime(f"{date_str} {end_str}", "%d %B %Y %I:%M%p")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    closure_times.append((start_dt, end_dt))
                    _LOGGER.info("Parsed Format 3 closure: %s to %s", start_dt, end_dt)
                    continue
                except Exception as e:
                    _LOGGER.error("Error parsing format 3 time: %s", e)

            match4 = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)\s+to\s+(\d{1,2}:\d{2}\s*[ap]m)', text, re.I)
            if match4 and current_explicit_date:
                try:
                    start_str = match4.group(1).lower()
                    end_str = match4.group(2).lower()
                    date_str = current_explicit_date.strftime("%d %B %Y")
                    start_dt = datetime.strptime(f"{date_str} {start_str}", "%d %B %Y %I:%M%p")
                    end_dt = datetime.strptime(f"{date_str} {end_str}", "%d %B %Y %I:%M%p")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    closure_times.append((start_dt, end_dt))
                    _LOGGER.info("Parsed Format 4 closure: %s to %s", start_dt, end_dt)
                except Exception as e:
                    _LOGGER.error("Error parsing format 4 time: %s", e)

    _LOGGER.info("Total parsed closures: %d", len(closure_times))

    now = datetime.now()
    upcoming = [c for c in closure_times if c[1] > now]
    if upcoming:
        next_closure = min(upcoming, key=lambda c: c[0])
        bridge_closed = next_closure[0] <= now <= next_closure[1]
    elif not planned_closures:
        _LOGGER.info("Confirmed: No closures currently scheduled.")
        bridge_closed = False
    else:
        _LOGGER.info("No upcoming closures found after filtering by current time.")
        bridge_closed = False

    if not closure_times and planned_closures:
        _LOGGER.warning("No closure times were parsed from the page.")

    result = {
        'bridge_closed': bridge_closed,
        'next_closure_start': next_closure[0].isoformat() if next_closure else None,
        'next_closure_end': next_closure[1].isoformat() if next_closure else None,
        'closure_times': closure_times
    }

    _LOGGER.info("Renfrew Bridge: returning %s", result)
    return result
