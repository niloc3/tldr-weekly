import json, pathlib, datetime, itertools, collections
from transformers import pipeline

WEEK = 7
TOP_K = 12                # how many stories survive heuristics
OUT = pathlib.Path("site/_posts")  # Jekyll default

today = datetime.date.today()
weekago = today - datetime.timedelta(days=WEEK)

# 1️⃣ collect the last 7 days of bullet‑points
stories = []
for day in (weekago + datetime.timedelta(i) for i in range(WEEK)):
    print("📅", day)
    print(f"data/{day}")
    for f in pathlib.Path(f"data/{day}").glob("*.json"):
        blob = json.load(open(f))
        stories += [(b["title"], b["link"], b["content"]) for b in blob["items"]]

# 2️⃣ very cheap heuristics: score by duplicate URLs & day‑frequency
score = collections.Counter(url for _, url, _ in stories)
top = sorted(stories, key=lambda t: score[t[1]], reverse=True)[:TOP_K]

print(stories)

# 3️⃣ LLM compress titles+blurbs → one weekly summary
pipe = pipeline("summarization", model="mrm8488/t5-base-finetuned-summarize-news")
joined = "\n\n".join(f"{t}\n{c}" for t, _, c in top)
digest = pipe(joined, max_length=230, min_length=120, do_sample=False)[0]["summary_text"]

# 4️⃣ write markdown (Jekyll front‑matter)
fname = OUT / f"{today}.md"
with open(fname, "w") as f:
    f.write(f"---\nlayout: post\ntitle: 'TLDR Weekly Digest – {today}'\n---\n\n")
    f.write(digest + "\n\n---\n\n")
    for title, url, _ in top:
        f.write(f"* [{title}]({url})\n")
print("📝 weekly post created:", fname)
