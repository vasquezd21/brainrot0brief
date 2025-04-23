import requests
from datetime import datetime
from bs4 import BeautifulSoup

# --- Hacker News ---
def get_hackernews_top(n=5):
    url = "https://news.ycombinator.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".athing")[:n]
    posts = []

    for item in items:
        title_tag = item.select_one(".storylink")
        if not title_tag:
            continue  # skip if no title

        title = title_tag.text.strip()
        link = title_tag["href"]
        score_tag = item.find_next_sibling("tr").select_one(".score")
        score = score_tag.text if score_tag else "0 points"

        posts.append({
            "title": title,
            "link": link,
            "score": score
        })

    return posts


# --- Product Hunt ---
def get_producthunt_top(n=5):
    url = "https://www.producthunt.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        products = soup.select('ul[class*="styles_productsList"] li')[:n]
        result = []

        for item in products:
            name = item.select_one("h3")
            desc = item.select_one("p")
            if name and desc:
                result.append({
                    "name": name.text.strip(),
                    "description": desc.text.strip()
                })

        return result if result else []
    except Exception as e:
        print(f"❌ Failed to fetch Product Hunt: {e}")
        return []



def make_brainrot_digest(hn_posts, ph_posts):
    lines = []
    lines.append("# 🧠 The Weekly Brainrot Brief")
    lines.append(f"*{datetime.now().strftime('%A, %B %d, %Y')}*")
    lines.append("\n## 🔥 Hacker News Highlights\n")

    for post in hn_posts:
        lines.append(f"- **{post['title']}** — [{post['link']}]({post['link']}) ({post['score']})")

    lines.append("\n## 🚀 Product Hunt Picks\n")
    for product in ph_posts:
        lines.append(f"- **{product['name']}**: {product['description']}")

    lines.append("\n## 🧂 Closing Thought\n> Still no VC funding? Neither do we. At least you're smarter than 99% of LinkedIn.\n")

    return "\n".join(lines)


# run it all
hn_top = get_hackernews_top()
ph_top = get_producthunt_top()
digest = make_brainrot_digest(hn_top, ph_top)

digest = make_brainrot_digest(hn_top, ph_top)
with open("weekly_brainrot.md", "w") as f:
    f.write(digest)

print("✅ newsletter saved as weekly_brainrot.md")

with open("weekly_brainrot.md", "w") as f:
    f.write(digest)

print("✅ newsletter saved as weekly_brainrot.md")
print("\n📬 Here's your Brainrot Brief:\n")
print(digest)