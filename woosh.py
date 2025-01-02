from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os

# Funktion, um das Indexverzeichnis zu erstellen
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

# Schema des Indexes definieren
schema = Schema(
    url=ID(stored=True, unique=True),  # Eindeutige URL
    title=TEXT(stored=True),           # Titel der Seite
    content=TEXT                       # Inhalt der Seite
)

# Index erstellen
ix = create_in(index_dir, schema)
writer = ix.writer()

# Funktion, um Daten aus dem Crawler hinzuzufügen
def add_crawler_data_to_index(crawler_index):
    for url, page_data in crawler_index.items():
        title = page_data.get("title", "No Title")  # Standardtitel, falls keiner gefunden wurde
        content = page_data.get("content", "")       # Seiteninhalt
        writer.add_document(url=url, title=title, content=content)

# Beispiel: Crawler-Index-Daten simulieren
# (Später wird diese Struktur von deinem Crawler befüllt)
crawler_index = {
    "https://vm009.rz.uos.de/crawl/index.html": {
        "title": "Startseite",
        "content": "Willkommen auf der Startseite. Dies ist ein Testwebsite-Inhalt."
    },
    "https://vm009.rz.uos.de/crawl/page2.html": {
        "title": "Zweite Seite",
        "content": "Dies ist die zweite Seite. Sie enthält weitere Inhalte."
    },
    "https://vm009.rz.uos.de/crawl/page3.html": {
        "title": "Dritte Seite",
        "content": "Die dritte Seite handelt von Crawlern und Suchmaschinen."
    }
}

# Daten dem Index hinzufügen
add_crawler_data_to_index(crawler_index)

# Änderungen speichern
writer.commit()

# Suchfunktion
with ix.searcher() as searcher:
    print("\nSuche im Index:")
    query_input = "Crawler Suchmaschinen"
    query = QueryParser("content", ix.schema).parse(query_input)
    results = searcher.search(query)

    print(f"Suchergebnisse für: '{query_input}'")
    for result in results:
        print(f"URL: {result['url']}, Titel: {result['title']}")