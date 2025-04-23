import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import openai
import os
from dotenv import load_dotenv

# Load .env and set OpenRouter config
load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")

openai.base_url = "https://openrouter.ai/v1"


def generate_gpt_comment(prompt, model="mistralai/mistral-small-3.1-24b-instruct", max_tokens=60):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You're a sarcastic but insightful newsletter writer. Keep responses short, punchy, and slightly funny."},
                {"role": "user", "content": f"Write a one-liner comment for this:\n\n{prompt}"}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.8
        }

        print("=== OUTGOING PAYLOAD ===")
        print(json.dumps(payload, indent=2))

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        print("=== RESPONSE STATUS ===")
        print(response.status_code)
        print("=== RESPONSE TEXT ===")
        print(response.text)

        response.raise_for_status()
        result = response.json()
        return "✏️ *Comment:* " + result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"⚠️ (Error getting comment: {e})"



# === SCRAPERS ===
def fetch_hackernews_top(n=5):
    url = "https://hn.algolia.com/api/v1/search?tags=front_page"
    res = requests.get(url)
    hits = res.json().get("hits", [])[:n]
    return [{"title": h["title"], "link": h["url"] or h["story_url"]} for h in hits]

def scrape_reddit_top(subs=["AskReddit", "ChatGPT", "technology"], limit=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    posts = []
    for sub in subs:
        url = f"https://www.reddit.com/r/{sub}/top/?t=week"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        # Select the entire anchor tag for the post
        post_elements = soup.select("div.Post div.contents a.Post__title") 
        count = 0
        for post_element in post_elements:
            text = post_element.text.strip()
            if text.lower() != "community highlights" and count < limit:
                permalink = post_element['href']  # Extract the permalink
                posts.append({
                    "title": text,
                    "subreddit": sub,
                    "link": f"https://reddit.com{permalink}" # Construct full link
                })
                count += 1
    return posts

def fetch_toolify_top(n=3):
    url = "https://www.toolify.ai/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    cards = soup.select(".product-card")[:n]
    tools = []
    for card in cards:
        name_tag = card.select_one("h3")
        desc_tag = card.select_one("p")
        link_tag = card.select_one("a")
        if name_tag and desc_tag and link_tag:
            tools.append({
                "name": name_tag.text.strip(),
                "description": desc_tag.text.strip(),
                "link": "https://www.toolify.ai" + link_tag["href"]
            })
    return tools

# === FORMAT NEWSLETTER ===
def build_newsletter(data):
    lines = [f"# 💠 The Weekly Brainrot Brief", f"*{datetime.now().strftime('%A, %B %d, %Y')}*\n"]

    lines.append("## 🔥 Hacker News Highlights")
    for post in data["hackernews"]:
        comment = generate_gpt_comment(post['title'])
        lines.append(f"- **{post['title']}**\n  [{post['title']}]({post['link']})\n  {comment}") # For Hacker News

    lines.append("\n## 🧵 Reddit Brainrot")
    for post in data["reddit"]:
         lines.append(f"- **[{post['subreddit']}] {post['title']}** — [{post['title']}]({post['link']})") # For Reddit

    lines.append("\n## 🧪 Trending Tools (Toolify)")
    for tool in data["toolify"]:
        prompt = f"{tool['name']}: {tool['description']}"
        comment = generate_gpt_comment(prompt)
        lines.append(f"- **{tool['name']}**: {tool['description']}\n  [{tool['name']}]({tool['link']})\n  {comment}") # For Toolify


    lines.append("\n## 🥂 Closing Thought")
    lines.append("> Still no VC funding? Just vibes. You’re doing better than most tech CEOs.")
    return "\n\n".join(lines)

# === MAIN ===
def main():
    data = {
        "hackernews": fetch_hackernews_top(),
        "reddit": scrape_reddit_top(),
        "toolify": fetch_toolify_top()
    }

    today = datetime.now().strftime('%Y-%m-%d')
    with open(f"brainrot_scrape_{today}.json", "w") as f:
        json.dump(data, f, indent=2)

    newsletter = build_newsletter(data)
    with open(f"weekly_brainrot_full_{today}.md", "w") as f:
        f.write(newsletter)

    print(f"✅ Newsletter ready: weekly_brainrot_full_{today}.md")

if __name__ == "__main__":
    main()