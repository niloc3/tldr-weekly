import feedparser, bs4, pathlib, datetime, json

RSS = "https://tldrnewsletter.substack.com/feed"
OUT = pathlib.Path("data")
OUT.mkdir(exist_ok=True)

today = datetime.date.today().isoformat() 
d = feedparser.parse(RSS)

print(today)
tmp = d.entries
for e in tmp:
    print(e.summary.split(" ")[1])

# Get today's entry
entry = next(e for e in d.entries if today in e.summary.split(" ")[1])

html = None
if "content" in entry and entry.content:          # preferred
    html = entry.content[0].value
else:                                            # fallback
    html = entry.summary
# --------------------------

# --- NEW: parse the newsletter's <li> bullets into items -------------
soup = bs4.BeautifulSoup(html, "html.parser")
items = []

for h4 in soup.find_all("h4"):
    a = h4.find("a")
    if a is None:
        continue                                # skip odd headings

    title = a.get_text(strip=True)
    link  = a["href"]

    # The summary paragraph is the very next <p>
    p = h4.find_next_sibling("p")
    content = p.get_text(" ", strip=True) if p else ""

    items.append({"title": title, "link": link, "content": content})
print(f"found {len(items)} bullet items")

# ---------------------------------------------------------------------

blob = {
    "date": today,
    "category": "tech",        # or derive from title if you want
    "items": items,
}

# Save under data/<date>/rss.json to match the old folder layout
dest = OUT / today
dest.mkdir(exist_ok=True)
with open(dest / "rss.json", "w") as f:
    json.dump(blob, f, indent=2)

print(f"✅ saved {len(items)} items for {today}")
