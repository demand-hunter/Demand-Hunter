import feedparser

RSS_FEEDS = [
    "https://www.reddit.com/r/Entrepreneur/.rss",
    "https://www.reddit.com/r/sidehustle/.rss",
    "https://www.reddit.com/r/freelance/.rss"
]

def coletar_posts():

    posts = []

    for feed_url in RSS_FEEDS:

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:

                posts.append({
                    "titulo": entry.title,
                    "link": entry.link,
                    "resumo": entry.summary if hasattr(entry, "summary") else ""
                })

        except Exception as e:
            print(f"Erro no feed: {e}")

    return posts