"""
Twitter/X Scraper pakai Playwright + cookies.json
Output format SAMA dengan data temen:
Author_Username, Tweet_Text, Mentions, Reply_To, Quote_Tweet_Of, Engagement

Flow: Search keyword → scroll → ambil tweet → masuk tiap tweet ambil reply

REQUIREMENTS:
    pip install playwright
    playwright install chromium

PERSIAPAN:
    1. Export cookies dari browser X (pakai extension "Cookie-Editor" atau sejenis)
    2. Save sebagai 'cookies.json' di folder yang sama dengan script ini
"""

import json
import time
import csv
from playwright.sync_api import sync_playwright

# ============================================================
# KONFIGURASI
# ============================================================
KEYWORD = "RUU TNI"
MAX_SCROLLS_SEARCH = 5        # Scroll di halaman search
OPEN_TWEETS_FOR_REPLIES = True # True = masuk tiap tweet ambil reply (lebih banyak data)
MAX_TWEETS_TO_OPEN = 5        # Berapa tweet yang dibuka untuk ambil reply
MAX_SCROLLS_REPLY = 5          # Scroll di halaman reply per tweet
OUTPUT_FILE = "contoh.csv"
COOKIES_FILE = "cookies.json"
# ============================================================


def filter_cookies(cookies):
    """Bersihkan cookies dari field yang Playwright tidak terima"""
    filtered = []
    for cookie in cookies:
        c = cookie.copy()
        if 'sameSite' in c:
            if c['sameSite'] == 'no_restriction' or c['sameSite'] is None:
                c['sameSite'] = 'None'
            elif c['sameSite'] == 'lax':
                c['sameSite'] = 'Lax'
            elif c['sameSite'] == 'strict':
                c['sameSite'] = 'Strict'
        keys_to_remove = ['hostOnly', 'session', 'firstPartyDomain', 'partitionKey', 'storeId']
        for key in keys_to_remove:
            if key in c:
                del c[key]
        filtered.append(c)
    return filtered


def extract_tweet_data(article):
    """Extract data dari satu article tweet, return dict dengan format temen"""
    data = {
        "Author_Username": "",
        "Tweet_Text": "",
        "Mentions": "",
        "Reply_To": "",
        "Quote_Tweet_Of": "",
        "Engagement": ""
    }
    
    # 1. Author_Username
    try:
        user_blocks = article.locator('[data-testid="User-Name"]').all()
        if user_blocks:
            texts = user_blocks[0].inner_text().split('\n')
            for t in texts:
                if t.startswith('@'):
                    data["Author_Username"] = t
                    break
    except:
        pass

    # 2. Tweet_Text & 3. Mentions
    try:
        tweet_text_elem = article.locator('[data-testid="tweetText"]')
        if tweet_text_elem.count() > 0:
            data["Tweet_Text"] = tweet_text_elem.first.inner_text()
            mention_elems = tweet_text_elem.first.locator('a[href^="/"]').all()
            mentions = [m.inner_text() for m in mention_elems if m.inner_text().startswith('@')]
            data["Mentions"] = ", ".join(mentions)
    except:
        pass

    # 4. Reply_To
    try:
        reply_texts = article.locator('text=/Replying to/').all_inner_texts()
        if reply_texts:
            for w in reply_texts[0].split():
                if w.startswith('@'):
                    data["Reply_To"] = w
                    break
    except:
        pass

    # 5. Quote_Tweet_Of
    try:
        user_blocks = article.locator('[data-testid="User-Name"]').all()
        if len(user_blocks) > 1:
            texts = user_blocks[1].inner_text().split('\n')
            for t in texts:
                if t.startswith('@'):
                    data["Quote_Tweet_Of"] = t
                    break
    except:
        pass

    # 6. Engagement
    try:
        replies = article.locator('[data-testid="reply"]').first.inner_text() if article.locator('[data-testid="reply"]').count() > 0 else "0"
        retweets = article.locator('[data-testid="retweet"]').first.inner_text() if article.locator('[data-testid="retweet"]').count() > 0 else "0"
        likes = article.locator('[data-testid="like"]').first.inner_text() if article.locator('[data-testid="like"]').count() > 0 else "0"
        data["Engagement"] = f"Replies: {replies}, Retweets: {retweets}, Likes: {likes}"
    except:
        pass
    
    return data


def get_tweet_url(article):
    """Ambil URL tweet dari article (untuk dibuka cari reply)"""
    try:
        link_elem = article.locator('a[href*="/status/"]').first
        href = link_elem.get_attribute("href")
        if href and "/status/" in href:
            return f"https://x.com{href}" if href.startswith("/") else href
    except:
        pass
    return None


def scrape_search(page, keyword, max_scrolls, writer, seen_tweets):
    """Scrape halaman search, return list URL tweet untuk dibuka lagi"""
    search_url = f'https://x.com/search?q={keyword.replace(" ", "%20")}&src=typed_query&f=live'
    print(f"\n[SEARCH] {keyword}")
    page.goto(search_url)
    time.sleep(5)
    
    tweet_urls = []
    saved = 0
    
    for i in range(max_scrolls):
        print(f"  Scroll {i+1}/{max_scrolls}...")
        articles = page.locator('article[data-testid="tweet"]').all()
        
        for article in articles:
            try:
                data = extract_tweet_data(article)
                
                if data["Tweet_Text"] and data["Tweet_Text"] not in seen_tweets:
                    seen_tweets.add(data["Tweet_Text"])
                    writer.writerow(data)
                    saved += 1
                    
                    # Simpan URL untuk dibuka cari reply (kalau dia OP, bukan reply)
                    if OPEN_TWEETS_FOR_REPLIES and not data["Reply_To"]:
                        url = get_tweet_url(article)
                        if url and url not in tweet_urls:
                            tweet_urls.append(url)
            except:
                continue
        
        page.mouse.wheel(0, 2500)
        time.sleep(3)
    
    print(f"  → {saved} tweet baru dari search")
    return tweet_urls[:MAX_TWEETS_TO_OPEN]


def scrape_replies(page, tweet_url, max_scrolls, writer, seen_tweets):
    """Buka satu tweet, scroll, ambil semua reply"""
    try:
        page.goto(tweet_url, timeout=30000)
        time.sleep(4)
    except:
        return 0
    
    saved = 0
    for i in range(max_scrolls):
        articles = page.locator('article[data-testid="tweet"]').all()
        
        for article in articles:
            try:
                data = extract_tweet_data(article)
                
                if data["Tweet_Text"] and data["Tweet_Text"] not in seen_tweets:
                    seen_tweets.add(data["Tweet_Text"])
                    writer.writerow(data)
                    saved += 1
            except:
                continue
        
        page.mouse.wheel(0, 2500)
        time.sleep(2)
    
    return saved


def main():
    # 1. Load cookies
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {COOKIES_FILE} tidak ditemukan!")
        return

    # 2. Setup CSV
    csv_file = open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8')
    fieldnames = ['Author_Username', 'Tweet_Text', 'Mentions', 'Reply_To', 'Quote_Tweet_Of', 'Engagement']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    seen_tweets = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(filter_cookies(cookies))
        page = context.new_page()
        
        print("Mencoba masuk ke X menggunakan Cookie...")
        
        # PHASE 1: Search
        tweet_urls = scrape_search(page, KEYWORD, MAX_SCROLLS_SEARCH, writer, seen_tweets)
        
        # PHASE 2: Buka tiap tweet, ambil reply
        if OPEN_TWEETS_FOR_REPLIES and tweet_urls:
            print(f"\n[REPLIES] Membuka {len(tweet_urls)} tweet untuk ambil reply...")
            for idx, url in enumerate(tweet_urls, 1):
                print(f"  [{idx}/{len(tweet_urls)}] {url}")
                added = scrape_replies(page, url, MAX_SCROLLS_REPLY, writer, seen_tweets)
                print(f"      → {added} reply baru")
                time.sleep(2)
        
        browser.close()
    
    csv_file.close()
    
    print(f"\n{'=' * 60}")
    print(f"DONE! Total tweet unik: {len(seen_tweets)}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
