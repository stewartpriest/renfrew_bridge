from bs4 import BeautifulSoup
import cloudscraper
import re
from datetime import datetime, timedelta
import logging
import dateparser

_LOGGER = logging.getLogger(__name__)

def get_bridge_status(options=None):
    _LOGGER.info("Renfrew Bridge: get_bridge_status called")

    url = 'https://www.renfrewshire.gov.uk/renfrew-bridge'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        _LOGGER.error("Failed to fetch page from %s: %s", url, e)
        return {
            'bridge_closed': False,
            'next_closure_start': None,
            'next_closure_end': None,
            'current_closure_end': None,
            'closure_times': []
        }

    soup = BeautifulSoup(response.content, 'html.parser')
    newsflash_div = soup.find('div', class_='newsflash__padding') or soup.find('div', class_='textblock')
    if not newsflash_div:
        _LOGGER.warning("Could not find expected content container. Page structure may have changed.")
        return {
            'bridge_closed': False,
            'next_closure_start': None,
            'next_closure_end': None,
            'current_closure_end': None,
            'closure_times': []
        }

    paragraphs = newsflash_div.find_all(['p', 'li', 'div'])
    closure_times = []
    current_explicit_date = None

    def already_parsed(start_dt, end_dt):
        return any(existing_start == start_dt and existing_end == end_dt for existing_start, existing_end in closure_times)

    def parse_time_range(text, date_context):
        pattern = re.compile(
            r'(?:from\s+)?'
            r'(\d{1,2}(?::\d{2})?)\s*(am|pm)?'
            r'\s*(?:to|until|-)\s*'
            r'(\d{1,2}(?::\d{2})?)\s*(am|pm)?',
            re.IGNORECASE
        )

        match = pattern.search(text)
        if not match:
            fallback = re.findall(r'(\d{1,2}(?::\d{2})?)\s*(am|pm)?', text, re.IGNORECASE)
            if len(fallback) >= 2:
                start_raw, start_ampm = fallback[0]
                end_raw, end_ampm = fallback[1]
            else:
                return None, None
        else:
            start_raw, start_ampm, end_raw, end_ampm = match.groups()

        def parse_time(t_str, ampm, context_date):
            if len(t_str) == 4 and ':' not in t_str:
                t_str = f"{t_str[:2]}:{t_str[2:]}"
            time_str = f"{t_str} {ampm}" if ampm else t_str
            return dateparser.parse(time_str, settings={'RELATIVE_BASE': context_date})

        base_date = datetime.combine(date_context, datetime.min.time())
        start_dt = parse_time(start_raw, start_ampm, base_date)
        end_dt = parse_time(end_raw, end_ampm, base_date)

        if start_dt and end_dt and end_dt < start_dt:
            end_dt += timedelta(days=1)

        return start_dt, end_dt

    for p in paragraphs:
        text = p.get_text(separator=" ", strip=True)
        text = text.replace("\xa0", " ").replace("  ", " ").strip().lower()

        # Normalize time delimiters and suffixes
        text = text.replace(";", ":")  # fix semicolon
        text = re.sub(r'(\d{1,2})\.(\d{2})', r'\1:\2', text)  # fix dot-based times
        text = re.sub(r'(\d{1,2}:\d{2})([ap]m)', r'\1 \2', text)  # ensure space before am/pm
        text = text.replace("a.m.", "am").replace("p.m.", "pm")
        text = text.replace("–", "-").replace("—", "-")  # normalize dashes

        _LOGGER.debug("Raw line: '%s'", text)

        # Skip metadata lines
        if re.search(r'last\s+updated', text, re.IGNORECASE):
            _LOGGER.debug("Skipping metadata line: %s", text)
            continue

        # Strip weekday prefix if present
        if re.match(r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s', text, re.IGNORECASE):
            text = re.sub(r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+', '', text, flags=re.IGNORECASE)

        standalone_date = dateparser.parse(
            text,
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
                "DATE_ORDER": "DMY"
            }
        )

        if standalone_date:
            current_explicit_date = standalone_date.date()
            _LOGGER.debug("Set current_explicit_date: %s", current_explicit_date)
            continue

        if current_explicit_date:
            try:
                start_dt, end_dt = parse_time_range(text, current_explicit_date)
                if start_dt and end_dt:
                    duration = (end_dt - start_dt).total_seconds()
                    if duration > 0 and duration < 86400:  # less than 24 hours
                        if not already_parsed(start_dt, end_dt):
                            closure_times.append((start_dt, end_dt))
                            _LOGGER.info("Parsed closure: %s to %s", start_dt, end_dt)
                    else:
                        _LOGGER.warning("Discarded suspicious closure range: %s to %s", start_dt, end_dt)
                else:
                    _LOGGER.warning("Could not parse time range from line: '%s'", text)
            except Exception as e:
                _LOGGER.error("Error parsing time range: %s", e)

    closure_times.sort(key=lambda c: c[0])

    now = datetime.now()
    bridge_closed = False
    current_closure_end_time = None
    next_closure = None

    for start, end in closure_times:
        if start <= now <= end:
            bridge_closed = True
            current_closure_end_time = end
            break

    upcoming = [c for c in closure_times if c[0] > now]
    if upcoming:
        next_closure = min(upcoming, key=lambda c: c[0])

    result = {
        'bridge_closed': bridge_closed,
        'next_closure_start': next_closure[0].isoformat() if next_closure else None,
        'next_closure_end': next_closure[1].isoformat() if next_closure else None,
        'current_closure_end': current_closure_end_time.isoformat() if current_closure_end_time else None,
        'closure_times': closure_times
    }

    _LOGGER.info("Renfrew Bridge: returning %s", result)
    return result
