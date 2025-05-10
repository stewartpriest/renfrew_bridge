
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta


def get_bridge_status():
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
        current_date = None

        for p in paragraphs:
            text = p.get_text(strip=True)
            lowered = text.lower()

            if "no closure currently planned" in lowered:
                planned_closures = False

            elif "last updated" in lowered:
                match = re.match(r'last updated\s*[-–]?\s*(.+)', text, flags=re.I)
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

            elif re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', lowered):
                date_match = re.search(r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(\d{1,2})(st|nd|rd|th)?\s+([a-zA-Z]+)', text)
                if date_match:
                    day = int(date_match.group(2))
                    month = date_match.group(4)
                    try:
                        year = datetime.now().year
                        parsed = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
                        if parsed.month == 1 and datetime.now().month == 12:
                            parsed = parsed.replace(year=year + 1)
                        current_date = parsed
                    except ValueError:
                        current_date = None

            elif current_date and re.search(r'\d{1,2}:\d{2}\s*(am|pm)?\s*to\s*\d{1,2}:\d{2}\s*(am|pm)?', lowered):
                time_ranges = re.findall(r'(\d{1,2}:\d{2}\s*[ap]m?)\s*to\s*(\d{1,2}:\d{2}\s*[ap]m?)', text, flags=re.I)
                for start_str, end_str in time_ranges:
                    try:
                        start_dt = datetime.strptime(start_str.strip(), "%I:%M%p").replace(
                            year=current_date.year, month=current_date.month, day=current_date.day)
                        end_dt = datetime.strptime(end_str.strip(), "%I:%M%p").replace(
                            year=current_date.year, month=current_date.month, day=current_date.day)
                        if end_dt < start_dt:
                            end_dt += timedelta(days=1)
                            if end_dt.month == 1 and start_dt.month == 12:
                                end_dt = end_dt.replace(year=end_dt.year + 1)
                        closure_times.append((start_dt, end_dt))
                    except ValueError:
                        pass

    now = datetime.now()
    upcoming = [c for c in closure_times if c[1] > now]
    if upcoming:
        next_closure = min(upcoming, key=lambda c: c[0])
        bridge_closed = next_closure[0] <= now <= next_closure[1]
    else:
        bridge_closed = False

    return {
        'bridge_closed': bridge_closed,
        'next_closure_start': next_closure[0].isoformat() if next_closure else None,
        'next_closure_end': next_closure[1].isoformat() if next_closure else None
    }
