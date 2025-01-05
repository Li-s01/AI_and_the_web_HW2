from flask import Flask, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os

app = Flask(__name__)

# Funktion zum Überprüfen des Index
def get_index():
    index_dir = "indexdir"
    if os.path.exists(index_dir):
        return open_dir(index_dir)
    else:
        raise FileNotFoundError("Der Whoosh-Index wurde nicht gefunden. Bitte führen Sie zuerst den Crawler aus.")

# Startseite mit Suchformular
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Suchmaschine</title></head>
    <body>
        <h1>Willkommen zur Suchmaschine</h1>
        <form action="/search" method="post">
            <input type="text" name="query" placeholder="Suchbegriff eingeben" required>
            <button type="submit">Suchen</button>
        </form>
    </body>
    </html>
    """

# Suchroute, die den Suchbegriff verarbeitet und Ergebnisse anzeigt
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')  # Suchbegriff
    try:
        ix = get_index()
        with ix.searcher() as searcher:
            query_obj = QueryParser("content", ix.schema).parse(query)
            results = searcher.search(query_obj)

            # HTML-Ausgabe
            results_html = f"<h1>Suchergebnisse für: {query}</h1><ul>"
            for result in results:
                url = result["url"]
                title = result["title"]
                results_html += f'<li><a href="{url}">{title}</a></li>'
            results_html += "</ul><a href='/'>Zurück zur Suche</a>"

            return results_html

    except FileNotFoundError as e:
        return f"<h1>Fehler</h1><p>{str(e)}</p><a href='/'>Zurück</a>"
    except Exception as e:
        return f"<h1>Fehler</h1><p>Es ist ein Fehler aufgetreten: {str(e)}</p><a href='/'>Zurück</a>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
