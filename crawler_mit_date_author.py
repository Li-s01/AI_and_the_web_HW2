import requests
from bs4 import BeautifulSoup
from whoosh.index import open_dir
from whoosh.fields import Schema, TEXT, ID, DATETIME
from datetime import datetime
import os

# Basis-URL für die Website
prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix + 'index.html'

# Funktion zum Erstellen des Index-Verzeichnisses und Schema
def create_index():
    index_dir = "indexdir"
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

        schema = Schema(
            url=ID(stored=True, unique=True), # Eindeutige URL
            title=TEXT(stored=True),           # Titel der Seite
            content=TEXT(stored=True),         # Inhalt der Seite
            date=DATETIME(stored=True),
            author=TEXT(stored=True)
        )
        from whoosh.index import create_in
        create_in(index_dir, schema)
        print(f"Whoosh-Index wurde im Verzeichnis '{index_dir}' erstellt.")
    else:
        print(f"Indexverzeichnis '{index_dir}' existiert bereits.")
    return index_dir

# Funktion zum Crawlen und Indexieren
def crawl_and_index():
    # Stelle sicher, dass der Index existiert
    index_dir = create_index()
    ix = open_dir(index_dir)

    # Crawler-Logik
    stack = [start_url]
    visited = set()

    with ix.writer() as writer:
        while stack:
            url = stack.pop()
            if url not in visited:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")

                        # Daten sammeln
                        title = soup.title.string if soup.title else "No Title"
                        content = soup.get_text()
                        date_text = soup.date.string if soup.date else "No Date"
                        author = soup.author.string if soup.author else  "No Author"

                        # Umwandlung von date_text in ein datetime-Objekt 
                        try: 
                            date = datetime.strptime(date_text, "%Y-%m-%d") 
                        except ValueError: 
                            date = datetime.utcnow() # Fallback, falls das Datum nicht korrekt ist

                        # Zum Index hinzufügen
                        writer.update_document(
                            url=url,
                            title=title,
                            content=content,
                            date=date,
                            author=author
                        )
                        print(f"Indexiert: {url}")

                        # Links sammeln
                        for link in soup.find_all("a", href=True):
                            href = link["href"]
                            #href.startswith(prefix) and href not in visited:
                            stack.append(prefix + href)     # prefix + page1.html u.ä.

                        visited.add(url) 
                except Exception as e:
                    print(f"Fehler beim Abrufen der URL {url}: {e}")

    print("Crawling und Indexierung abgeschlossen.")

if __name__ == "__main__":
    crawl_and_index()