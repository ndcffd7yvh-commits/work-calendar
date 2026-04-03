import os
import io
import uuid
import pandas as pd
from datetime import timedelta
import requests

DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]
DROPBOX_FILENAME = "planning 2026.xlsx"


def find_file(token, filename):
    resp = requests.post(
        "https://api.dropboxapi.com/2/files/search_v2",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"query": filename},
    )
    resp.raise_for_status()
    matches = resp.json().get("matches", [])
    for m in matches:
        path = m["metadata"]["metadata"].get("path_display", "")
        if path.lower().endswith(filename.lower()):
            print(f"Found file at: {path}")
            return path
    raise FileNotFoundError(f"Could not find '{filename}' on Dropbox. Matches: {matches}")


def download_from_dropbox(token, path):
    resp = requests.post(
        "https://content.dropboxapi.com/2/files/download",
        headers={
            "Authorization": f"Bearer {token}",
            "Dropbox-API-Arg": f'{{"path": "{path}"}}',
        },
    )
    resp.raise_for_status()
    return io.BytesIO(resp.content)


def extract_abdel_events(file_bytes):
    df = pd.read_excel(file_bytes, sheet_name="Planning", header=None)
    abdel_data = df.iloc[3:][[4, 7]].copy()
    abdel_data.columns = ["date", "event"]
    abdel_data = abdel_data.dropna(subset=["date"])
    abdel_data = abdel_data[abdel_data["event"].notna()]
    abdel_data = abdel_data[abdel_data["event"] != "Abdel"]
    abdel_data["event"] = abdel_data["event"].astype(str).str.strip()
    abdel_data["date"] = pd.to_datetime(abdel_data["date"]).dt.date
    return abdel_data.sort_values("date").to_dict("records")


def group_events(rows):
    events = []
    i = 0
    while i < len(rows):
        start = rows[i]["date"]
        name = rows[i]["event"]
        end = start
        j = i + 1
        while j < len(rows):
            gap = (rows[j]["date"] - end).days
            if rows[j]["event"] == name and gap <= 3:
                end = rows[j]["date"]
                j += 1
            else:
                break
        events.append({"summary": name, "start": start, "end": end})
        i = j
    return events


def build_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Abdel Planning 2026//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Abdel Planning 2026",
        "X-WR-TIMEZONE:Europe/Brussels",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for ev in events:
        dtstart = ev["start"].strftime("%Y%m%d")
        dtend = (ev["end"] + timedelta(days=1)).strftime("%Y%m%d")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:{ev['summary']}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def main():
    print("Locating Excel file on Dropbox...")
    path = find_file(DROPBOX_TOKEN, DROPBOX_FILENAME)

    print("Downloading Excel from Dropbox...")
    file_bytes = download_from_dropbox(DROPBOX_TOKEN, path)

    print("Extracting Abdel's events...")
    rows = extract_abdel_events(file_bytes)

    print("Grouping consecutive events...")
    events = group_events(rows)

    print(f"Building ICS with {len(events)} events...")
    ics = build_ics(events)

    os.makedirs("output", exist_ok=True)
    with open("output/abdel.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print("Done! output/abdel.ics generated.")


if __name__ == "__main__":
    main()
