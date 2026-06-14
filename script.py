import json
import time
import csv
from playwright.sync_api import sync_playwright

def filter_cookies(cookies):
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

def scrape_with_cookies(keyword, max_scrolls=5):
    # 1. Buka dan baca file cookies yang sudah kamu ekspor tadi
    try:
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
    except FileNotFoundError:
        print("Error: File cookies.json tidak ditemukan!")
        return

    # 2. Siapkan file CSV untuk menyimpan hasil scraping
    csv_filename = "hasil_scraping_sna_2.csv"
    csv_file = open(csv_filename, mode='w', newline='', encoding='utf-8')
    fieldnames = ['Author_Username', 'Tweet_Text', 'Mentions', 'Reply_To', 'Quote_Tweet_Of', 'Engagement']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader() # Menulis baris judul (header) ke CSV

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Injeksi cookie
        context.add_cookies(filter_cookies(cookies))
        
        page = context.new_page()
        
        print("Mencoba masuk ke X menggunakan Cookie...")
        search_url = f'https://x.com/search?q={keyword}&src=typed_query'
        page.goto(search_url)
        time.sleep(5)
        
        print("Berhasil masuk! Memulai proses scraping...")
        seen_tweets = set() # Digunakan agar tidak ada data ganda (duplikat)
        total_saved = 0
        
        for i in range(max_scrolls):
            print(f"Scroll ke-{i+1} dari {max_scrolls}...")
            articles = page.locator('article[data-testid="tweet"]').all()
            
            for article in articles:
                try:
                    data = {
                        "Author_Username": "",
                        "Tweet_Text": "",
                        "Mentions": "",
                        "Reply_To": "",
                        "Quote_Tweet_Of": "",
                        "Engagement": ""
                    }
                    
                    # 1. Author_Username (Source Node)
                    try:
                        user_blocks = article.locator('[data-testid="User-Name"]').all()
                        if user_blocks:
                            texts = user_blocks[0].inner_text().split('\n')
                            for t in texts:
                                if t.startswith('@'):
                                    data["Author_Username"] = t
                                    break
                    except: pass

                    # 2. Tweet_Text & 3. Mentions
                    try:
                        tweet_text_elem = article.locator('[data-testid="tweetText"]')
                        if tweet_text_elem.count() > 0:
                            data["Tweet_Text"] = tweet_text_elem.first.inner_text()
                            
                            # Mentions (Target Node dari teks)
                            mention_elems = tweet_text_elem.first.locator('a[href^="/"]').all()
                            mentions = [m.inner_text() for m in mention_elems if m.inner_text().startswith('@')]
                            data["Mentions"] = ", ".join(mentions)
                    except: pass
                    
                    # 4. Reply_To
                    try:
                        reply_texts = article.locator('text=/Replying to/').all_inner_texts()
                        if reply_texts:
                            for w in reply_texts[0].split():
                                if w.startswith('@'):
                                    data["Reply_To"] = w
                                    break
                    except: pass

                    # 5. Quote_Tweet_Of
                    try:
                        user_blocks = article.locator('[data-testid="User-Name"]').all()
                        if len(user_blocks) > 1: # Jika ada 2 blok nama, yang kedua adalah Quote
                            texts = user_blocks[1].inner_text().split('\n')
                            for t in texts:
                                if t.startswith('@'):
                                    data["Quote_Tweet_Of"] = t
                                    break
                    except: pass

                    # 6. Engagement
                    try:
                        replies = article.locator('[data-testid="reply"]').first.inner_text() if article.locator('[data-testid="reply"]').count() > 0 else "0"
                        retweets = article.locator('[data-testid="retweet"]').first.inner_text() if article.locator('[data-testid="retweet"]').count() > 0 else "0"
                        likes = article.locator('[data-testid="like"]').first.inner_text() if article.locator('[data-testid="like"]').count() > 0 else "0"
                        data["Engagement"] = f"Replies: {replies}, Retweets: {retweets}, Likes: {likes}"
                    except: pass

                    # Simpan data jika tweet ini belum pernah disimpan sebelumnya
                    if data["Tweet_Text"] and data["Tweet_Text"] not in seen_tweets:
                        seen_tweets.add(data["Tweet_Text"])
                        writer.writerow(data)
                        total_saved += 1
                        
                except Exception as e:
                    continue
            
            # Scroll ke bawah perlahan untuk memuat tweet baru
            page.mouse.wheel(0, 2500)
            time.sleep(3)
            
        print(f"\nSelesai! Total tweet unik tersimpan: {total_saved}")
        print(f"File berhasil dibuat: {csv_filename}")
        
        browser.close()
        csv_file.close()

# Jalankan fungsi (Kamu bisa mengubah keyword atau jumlah scrollnya)
scrape_with_cookies("pemblokiran judol komdigi", max_scrolls=70)