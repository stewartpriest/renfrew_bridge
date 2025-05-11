
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

def get_bridge_status():
    _LOGGER.info("Renfrew Bridge: get_bridge_status called")

    url = 'https://www.renfrewshire.gov.uk/renfrew-bridge'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    newsflash_div = soup.find('div', class_='newsflash__padding')
    planned_closures = True
    closure_times = []
    last_updated_datetime = None
    next_closure = None
    bridge_closed = False

    if newsflash_div:
        paragraphs = newsflash_div.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            lowered = text.lower()

            if "no closure currently planned" in lowered:
                planned_closures = False

            elif "last updated" in lowered:
                match = re.search(r'last updated\s*[-–]?\s*(.+)', text, flags=re.I)
                if match:
                    cleaned = match.group(1).strip()
                    cleaned = re.sub(r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+', '', cleaned)
                    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', cleaned)
                    cleaned = re.sub(r'[^\w\s:apm]', '', cleaned, flags=re.I)
                    try:
                        year = datetime.now().year
                        cleaned_with_year = re.sub(r'(\d{1,2} \w+)\s+at', rf'\1 {year} at', cleaned)
                        last_updated_datetime = datetime.strptime(cleaned_with_year, "%d %B %Y at %I:%M%p")
                    except ValueError:
                        pass

            # New format: e.g. "Sunday 11th May from 09:15pm to 10:45pm"
            match = re.search(
                r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(\d{1,2})(st|nd|rd|th)?\s+([a-zA-Z]+)\s+from\s+(\d{1,2}:\d{2}\s*[ap]m)\s+to\s+(\d{1,2}:\d{2}\s*[ap]m)',
                text)
            if match:
                try:
                    day = int(match.group(2))
                    month = match.group(4)
                    start_time_str = match.group(5)
                    end_time_str = match.group(6)
                    year = datetime.now().year
                    start_dt = datetime.strptime(f"{day} {month} {year} {start_time_str}", "%d %B %Y %I:%M%p")
                    end_dt = datetime.strptime(f"{day} {month} {year} {end_time_str}", "%d %B %Y %I:%M%p")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    closure_times.append((start_dt, end_dt))
                except ValueError as e:
                    _LOGGER.error("Error parsing closure time: %s", e)

    now = datetime.now()
    upcoming = [c for c in closure_times if c[1] > now]
    if upcoming:
        next_closure = min(upcoming, key=lambda c: c[0])
        bridge_closed = next_closure[0] <= now <= next_closure[1]
    else:
        bridge_closed = False

    result = {
        'bridge_closed': bridge_closed,
        'next_closure_start': next_closure[0].isoformat() if next_closure else None,
        'next_closure_end': next_closure[1].isoformat() if next_closure else None
    }

    _LOGGER.info("Renfrew Bridge: returning %s", result)
    return result
