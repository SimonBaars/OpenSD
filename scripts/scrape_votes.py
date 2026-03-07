"""
scrape_votes.py - Scrape San Diego City Council vote results from Hyland AgendaOnline.

Fetches Results Summary HTML via the AJAX endpoint, parses the vote tables,
maps district numbers to council member names, and outputs structured JSON.

Usage:
    python scripts/scrape_votes.py
"""

import json
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://sandiego.hylandcloud.com/211agendaonlinecouncil"
MAIN_PAGE = f"{BASE_URL}/"
AJAX_URL = f"{BASE_URL}/Documents/ViewAgenda?meetingId={{meeting_id}}&type=summary&doctype=3"

DISTRICT_TO_MEMBER = {
    "1": "Joe LaCava",
    "2": "Jennifer Campbell",
    "3": "Stephen Whitburn",
    "4": "Henry Foster III",
    "5": "Marni von Wilpert",
    "6": "Kent Lee",
    "7": "Raul Campillo",
    "8": "Vivian Moreno",
    "9": "Sean Elo-Rivera",
}

ALL_DISTRICTS = set(DISTRICT_TO_MEMBER.keys())
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vote_records.json")


def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "SD-Council-Dashboard/1.0 (hackathon project)",
        "Accept": "text/html",
    })
    return s


def discover_meeting_ids(session):
    meeting_ids = []

    print("Fetching main Hyland page...")
    resp = session.get(MAIN_PAGE, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        match = re.search(r'ViewMeeting\?id=(\d+)&doctype=3', href)
        if match:
            mid = int(match.group(1))
            if mid not in meeting_ids:
                meeting_ids.append(mid)

    print(f"  Found {len(meeting_ids)} meetings on main page")

    # Probe backwards to find older meetings
    if meeting_ids:
        min_id = min(meeting_ids)
        print(f"  Probing for older meetings below ID {min_id}...")
        found_older = 0
        consecutive_misses = 0
        for mid in range(min_id - 1, min_id - 150, -1):
            try:
                url = AJAX_URL.format(meeting_id=mid)
                resp = session.get(url, timeout=10)
                if resp.ok and "RESULTS SUMMARY" in resp.text:
                    meeting_ids.append(mid)
                    found_older += 1
                    consecutive_misses = 0
                else:
                    consecutive_misses += 1
                if consecutive_misses > 25:
                    break
                time.sleep(0.15)
            except Exception:
                consecutive_misses += 1
        print(f"    Found {found_older} additional older meetings")

    meeting_ids.sort()
    return meeting_ids


def parse_vote_string(vote_str):
    if not vote_str or not vote_str.strip():
        return None

    vote_str = vote_str.strip()
    votes = {}

    if vote_str.lower().startswith("unanimous"):
        absent = set()
        for m in re.findall(r'(\d+)[\s-]*not[\s-]*present', vote_str, re.IGNORECASE):
            for ch in m:
                if ch.isdigit():
                    absent.add(ch)
        for d in ALL_DISTRICTS:
            votes[DISTRICT_TO_MEMBER[d]] = "absent" if d in absent else "yes"
        return votes

    parts = re.split(r';\s*', vote_str)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.match(r'^(\d+)\s*[-\u2013]\s*(.+)$', part)
        if match:
            digits = match.group(1)
            action = match.group(2).strip().lower()
            vote_val = None
            if "yea" in action or "yes" in action or "aye" in action:
                vote_val = "yes"
            elif "nay" in action or "no" in action:
                vote_val = "no"
            elif "not present" in action or "absent" in action:
                vote_val = "absent"
            elif "abstain" in action or "recuse" in action:
                vote_val = "abstain"
            if vote_val:
                for ch in digits:
                    if ch in DISTRICT_TO_MEMBER:
                        votes[DISTRICT_TO_MEMBER[ch]] = vote_val

    if votes:
        for d, name in DISTRICT_TO_MEMBER.items():
            if name not in votes:
                votes[name] = "absent"

    return votes if votes else None


def parse_meeting_content(html, meeting_id):
    if "RESULTS SUMMARY" not in html:
        return []

    soup = BeautifulSoup(html, "lxml")
    records = []

    text = soup.get_text()
    date_str = "Unknown"
    date_match = re.search(r'DATE:\s*\w+,\s*(\w+\s+\d{1,2},?\s*\d{4})', text, re.IGNORECASE)
    if date_match:
        raw = date_match.group(1).strip().replace(",", "")
        try:
            dt = datetime.strptime(raw, "%B %d %Y")
            date_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            date_str = raw

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 6:
                continue

            cell_texts = [c.get_text(strip=True) for c in cells]
            item_no = cell_texts[0]
            action_text = cell_texts[1]
            vote_text = cell_texts[5]

            if not item_no or item_no in ("ITEMNO.", "ITEM NO."):
                continue
            if "QUIT" in action_text:
                continue
            if not vote_text:
                continue

            parsed_votes = parse_vote_string(vote_text)
            if not parsed_votes:
                continue

            records.append({
                "date": date_str,
                "item_number": item_no,
                "item_title": action_text,
                "votes": parsed_votes,
                "meeting_id": meeting_id,
            })

    return records


def main():
    session = get_session()
    meeting_ids = discover_meeting_ids(session)
    print(f"\nTotal meetings to scrape: {len(meeting_ids)}")

    if not meeting_ids:
        print("ERROR: No meetings found.")
        sys.exit(1)

    all_records = []
    for i, mid in enumerate(meeting_ids):
        print(f"  [{i+1}/{len(meeting_ids)}] Meeting {mid}...", end=" ", flush=True)
        try:
            url = AJAX_URL.format(meeting_id=mid)
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            records = parse_meeting_content(resp.text, mid)
            all_records.extend(records)
            print(f"{len(records)} items")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.3)

    print(f"\nTotal vote records: {len(all_records)}")
    unique_items = len(set(r["item_title"] for r in all_records))
    all_members = set()
    for r in all_records:
        all_members.update(r["votes"].keys())
    unique_dates = sorted(set(r["date"] for r in all_records))
    print(f"Unique agenda items: {unique_items}")
    print(f"Members: {', '.join(sorted(all_members))}")
    if unique_dates:
        print(f"Date range: {unique_dates[0]} to {unique_dates[-1]}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_records, f, indent=2)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
