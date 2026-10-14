import os, requests, feedparser
from urllib.parse import quote

SPOLKI = {
    "PKO BP": "PKO Bank Polski",
    "Orlen": "Orlen",
    "CD Projekt": "CD Projekt",
    # dodaj swoje: "skrót": "fraza do wyszukiwania"
}

def newsy(fraza):
    url = (f"https://news.google.com/rss/search?q={quote(fraza)}+when:1d"
           "&hl=pl&gl=PL&ceid=PL:pl")
    feed = feedparser.parse(url)
    return [f"- {e.title} ({e.get('source', {}).get('title', '')})"
            for e in feed.entries[:8]]

def streszczenie(tekst):
    prompt = (
        "Jesteś analitykiem giełdowym. Poniżej nagłówki z ostatnich 24h o spółkach z GPW. "
        "Dla każdej spółki napisz 1-3 zwięzłe punkty po polsku: wyniki finansowe, "
        "nowe rekomendacje (dom maklerski, cena docelowa), wypowiedzi zarządu, "
        "komunikaty ESPI, istotne wydarzenia. Jeśli nic ważnego, napisz 'brak istotnych informacji'. "
        "Niczego nie wymyślaj, opieraj się tylko na nagłówkach.\n\n" + tekst
    )
    r = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": os.environ["GEMINI_API_KEY"]},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def wyslij(tekst):
    requests.post(
        f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage",
        json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": tekst[:4000]},
        timeout=30,
    )

if __name__ == "__main__":
    blok = ""
    for nazwa, fraza in SPOLKI.items():
        blok += f"\n## {nazwa}\n" + "\n".join(newsy(fraza)) + "\n"
    wyslij("📈 Poranny przegląd GPW\n\n" + streszczenie(blok))
