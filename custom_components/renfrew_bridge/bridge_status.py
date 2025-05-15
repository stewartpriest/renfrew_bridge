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
            text = p.get_text(strip=True)
            text = text.replace("a.m.", "am").replace("p.m.", "pm").replace(".", "").lower()
            lowered = text.lower()

            if re.search(r'no\s+(further\s+)?closures?\s+(scheduled|planned)', lowered):
                planned_closures = False
                _LOGGER.info("Detected phrasing indicating no planned closures: '%s'", text)

            elif "last updated" in lowered:
                match = re.search(r'last updated\s*[-\u2013]?\s*(.+)', text, flags=re.I)
                if match:
                    cleaned = match.group(1).strip()
                    cleaned = re.sub(r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s*', '', cleaned)
                    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', cleaned)
                    cleaned = re.sub(r'[^\w\s:apm]', '', cleaned, flags=re.I)
                    try:
                        year = datetime.now().year
                        cleaned_with_year = re.sub(r'(\d{1,2} \w+)\s+at', rf'\1 {year} at', cleaned)
                        last_updated_datetime = datetime.strptime(cleaned_with_year, "%d %B %Y at %I:%M%p")
                    except ValueError:
                        pass

            # Extract date to carry forward to time-only entries
            date_match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s*(\d{1,2})(st|nd|rd|th)?\s+([a-zA-Z]+)', text, re.I)
            if date_match:
                try:
                    day = int(date_match.group(2))
                    month = date_match.group(4)
                    year = datetime.now().year
                    current_explicit_date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
                except ValueError:
                    pass

            match1 = re.search(
                r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)?(\d{1,2})(st|nd|rd|th)?\s+([a-zA-Z]+)\s*[-\u2013]?\s*(\d{1,2}:\d{2}\s*[ap]m)\s*(?:until|to)\s*(\d{1,2}:\d{2}\s*[ap]m)',
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
                except ValueError as e:
                    _LOGGER.error("Error parsing format 1 closure time: %s", e)

            match3 = re.search(
                r'(?:from\s*)?(\d{1,2}:\d{2}\s*[ap]\.??\s*m?)\s*(?:until|to)\s*(\d{1,2}:\d{2}\s*[ap]\.??\s*m?)',
                text,
                re.I
            )
            if match3:
                try:
                    start_time_str = re.sub(r'\.', '', match3.group(1).strip().lower().replace(' ', ''))
                    end_time_str = re.sub(r'\.', '', match3.group(2).strip().lower().replace(' ', ''))

                    target_date = current_explicit_date or datetime.now()
                    date_str = target_date.strftime("%d %B %Y")

                    for fmt in ["%H:%M", "%I:%M%p"]:
                        try:
                            start_dt = datetime.strptime(f"{date_str} {start_time_str}", f"%d %B %Y {fmt}")
                            end_dt = datetime.strptime(f"{date_str} {end_time_str}", f"%d %B %Y {fmt}")
                            if end_dt < start_dt:
                                end_dt += timedelta(days=1)
                            closure_times.append((start_dt, end_dt))
                            _LOGGER.info("Parsed Format 3 closure: %s to %s", start_dt, end_dt)
                            break
                        except ValueError:
                            continue
                    else:
                        _LOGGER.error("Failed to parse times in Format 3: %s to %s", start_time_str, end_time_str)
                except Exception as e:
                    _LOGGER.error("Error handling Format 3 time: %s", e)

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
        'next_closure_end': next_closure[1].isoformat() if next_closure else None
    }

    _LOGGER.info("Renfrew Bridge: returning %s", result)
    return result
