import requests
from bs4 import BeautifulSoup

# Basis-URL für die Website
prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix + 'index.html'

# Stack (Agenda) initialisieren: Beginne mit der Start-URL
stack = [start_url]
# Set zum Speichern der besuchten URLs
visited = set()
# Index (Wörter -> Seiten)
index = {}

# Crawler-Algorithmus
while stack:
    url = stack.pop()  # Nimm die nächste URL aus der Stack-Liste
    print("Besuche:", url)

    # Überprüfe, ob die URL schon besucht wurde
    if url not in visited:
        try:
            # Hole die Seite mit requests
            r = requests.get(url)
            if r.status_code == 200:  # Nur erfolgreiche Antworten verarbeiten
                print(f"Verarbeitete URL: {url}")
                
                # Markiere die URL als besucht
                visited.add(url)
                
                # Parsen des HTML-Inhalts mit BeautifulSoup
                soup = BeautifulSoup(r.content, 'html.parser')
                
                # Text extrahieren und in Wörter zerlegen
                words = soup.get_text().split()
                for word in words:
                    word = word.lower().strip()  # Kleinbuchstaben und Leerzeichen entfernen
                    if word not in index:
                        index[word] = []  # Wenn das Wort nicht existiert, erstelle eine neue Liste
                    if url not in index[word]:
                        index[word].append(url)  # Füge die URL für das Wort hinzu

                # Finde alle Links auf der Seite
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Wenn der Link auf der gleichen Domain ist und nicht besucht wurde, füge ihn zum Stack hinzu
                    if href.startswith(prefix) and href not in visited:
                        stack.append(href)
                        
        except Exception as e:
            print(f"Fehler beim Abrufen der URL {url}: {e}")
    else:
        print(f"URL bereits besucht: {url}")

# Gebe den erstellten Index aus
print("\nErstellter Index:")
for word, urls in index.items():
    print(f"{word}: {urls}")

# Suchfunktion
def search(index, query):
    query_words = query.lower().split()  # Zerlege den Suchbegriff in Wörter
    result_urls = []

    for word in query_words:
        if word in index:
            if not result_urls:
                result_urls = set(index[word])  # Starte mit den URLs des ersten Wortes
            else:
                result_urls = result_urls.intersection(set(index[word]))  # Schnittmenge der URLs finden

    return list(result_urls)  # Gib die gefundenen URLs zurück

# Interaktive Suchfunktion
print("\nTeste die Suchfunktion:")
while True:
    query = input("Gib Suchbegriffe ein (oder 'exit' zum Beenden): ")
    if query == "exit":
        break
    results = search(index, query)
    if results:
        print("Gefundene Seiten:")
        for url in results:
            print(f"- {url}")
    else:
        print("Keine Ergebnisse gefunden.")
