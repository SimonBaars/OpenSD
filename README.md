# Claude Community x City of SD Impact Lab

> **Disclaimer:** All data and resources linked below are subject to their respective terms of access and terms of service. Participants are responsible for reviewing and complying with applicable usage policies, licensing terms, API rate limits, and data use restrictions before accessing or incorporating any data into their projects.

# SD Council Voting Pattern Dashboard

**Team:** Michael Amin Iman  
**Hackathon:** Claude Community x City of SD Impact Lab (March 7, 2026)

---

## What's the Problem?

San Diego's city council votes on hundreds of agenda items every year — housing policy, public safety budgets, climate action, infrastructure spending — but there's no easy way for residents to see *how* their council members actually vote. The data exists on the City Clerk's website, buried inside a clunky government portal (Hyland AgendaOnline), spread across dozens of meeting pages, in a format that's basically unreadable.

**We fixed that.** We scraped it, cleaned it, and turned it into an interactive dashboard where you can see every vote, spot alliances, and actually understand what your council is doing.

---

## What It Does

An interactive, real-time dashboard that visualizes San Diego City Council voting patterns. Here's what you can explore:

### Dashboard (Home Page)
- **Voting Heatmap** — A D3.js heatmap showing all 9 council members on the Y-axis and every agenda item on the X-axis. Green = yes, red = no, yellow = abstain, gray = absent. Hover over any cell to see the full item title, date, and vote. You can immediately spot who votes together and who breaks from the pack.
- **Filter Bar** — Narrow down votes by date range, policy topic (Housing, Public Safety, Climate, etc.), or specific council member. The heatmap updates in real-time as you filter.
- **Alliance Matrix** — A 9×9 heatmap showing pairwise agreement rates between every pair of council members. Color-coded from red (low agreement ~50%) to green (high agreement ~100%). Hover to see exact percentages and shared vote counts.

### Council Members Page
- Grid of all 9 council members with their district numbers and official photos.
- Click any member to go to their profile.

### Member Profile Page
- Official photo, district number, AI-generated voting summary (when available)
- Policy breakdown showing how they vote across different topics
- Agreement rates with every other council member
- Full vote history table with color-coded badges

Click on any member name in the heatmap or matrix to jump straight to their profile.

---

## Data Sources

- **City Clerk Council Meeting Records** — [sandiego.hylandcloud.com](https://sandiego.hylandcloud.com/211agendaonlinecouncil/) — We scraped 18 council meetings from Dec 8, 2025 through Mar 3, 2026, pulling 275 agenda items and 2,475 individual vote records.
- **Council Member Info** — District numbers (1-9) and official photos from [sandiego.gov](https://www.sandiego.gov/)

All 9 current council members are covered:

| District | Member |
|----------|--------|
| 1 | Joe LaCava (Council President) |
| 2 | Jennifer Campbell |
| 3 | Stephen Whitburn |
| 4 | Henry Foster III |
| 5 | Marni von Wilpert |
| 6 | Kent Lee (President Pro Tem) |
| 7 | Raul Campillo |
| 8 | Vivian Moreno |
| 9 | Sean Elo-Rivera |

---

## How We Built It (Architecture)

```
┌─────────────────────────────────────────────┐
│  City Clerk (Hyland AgendaOnline)           │
│  sandiego.hylandcloud.com                   │
└────────────────┬────────────────────────────┘
                 │ Python scraper (requests + BeautifulSoup)
                 ▼
┌─────────────────────────────────────────────┐
│  data/vote_records.json (275 agenda items)  │
└────────────────┬────────────────────────────┘
                 │ seed_db.py
                 ▼
┌─────────────────────────────────────────────┐
│  SQLite Database (votes.db)                 │
│  - 2,475 vote rows                          │
│  - 9 members with districts + photos        │
│  - policy_tags table (Claude classification)│
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend (Python)                   │
│  GET /votes — filtered vote records         │
│  GET /members — council member list         │
│  GET /members/:id/profile — full profile    │
│  GET /heatmap — pairwise agreement rates    │
└────────────────┬────────────────────────────┘
                 │ Vite proxy (/api → :8000)
                 ▼
┌─────────────────────────────────────────────┐
│  React + Vite Frontend                      │
│  - D3.js VoteHeatmap (member × item grid)   │
│  - D3.js AllianceMatrix (9×9 agreement)     │
│  - FilterBar (date, topic, member)          │
│  - Member profiles with vote history        │
│  - Tailwind CSS styling                     │
└─────────────────────────────────────────────┘
```

### The Scraping Story

The City Clerk data wasn't straightforward. The main meeting pages load vote tables dynamically via JavaScript (AJAX calls to Hyland's backend). We had to:

1. Discover the hidden AJAX endpoint: `/Documents/ViewAgenda?meetingId={id}&type=summary&doctype=3`
2. Probe meeting IDs (they're not sequential) with a smart cutoff strategy
3. Parse 6-column HTML tables from the AJAX responses
4. Map cryptic district-number vote strings like `"12345689-yea; 7-nay"` to actual member names
5. Normalize vote values from `yea`/`nay`/`not present`/`recusal` into clean `yes`/`no`/`absent`/`abstain`

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| **Frontend** | React 19, Vite 7, D3.js, Recharts, Tailwind CSS v4, React Router |
| **Backend** | Python 3.14, FastAPI, uvicorn, aiosqlite |
| **Database** | SQLite |
| **Scraping** | Python requests, BeautifulSoup4 |
| **AI (optional)** | Anthropic Claude API — classifies agenda items into policy topics |
| **Dev Tools** | GitHub Copilot (Claude Opus 4.6), Node.js 25, npm 11 |

---

## Running It Locally

```bash
# Clone
git clone https://github.com/SimonBaars/city-of-sd-hackathon.git
cd city-of-sd-hackathon

# Backend
pip install -r backend/requirements.txt
python scripts/seed_db.py              # seed the database from scraped data
python -m uvicorn backend.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and explore.

---

## What's Next

- **Deploy** to Vercel (frontend) + Railway (backend) for a public demo
- **Claude classification** — run `scripts/classify_votes.py` with an Anthropic API key to auto-tag every agenda item by policy topic (Housing, Public Safety, Climate, etc.)
- **More meetings** — extend the scraper to pull historical data going back further
- **Voting trend charts** — time-series view of how member alignment shifts over months

---

*Built in a day at the Claude Community x City of SD Impact Lab hackathon. All data sourced from public San Diego City Clerk records.*

---

<details>
<summary>Original Hackathon Resources (click to expand)</summary>
