from flask import Flask, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import re


app = Flask(__name__)

# Funktion zum Überprüfen des Index
def get_index():
    index_dir = "indexdir"
    if os.path.exists(index_dir):
        return open_dir(index_dir)
    else:
        raise FileNotFoundError("Whoosh-Index not found. Start the crawler first.")

# Startseite mit Suchformular
@app.route('/')
def index():
    return """
  <!DOCTYPE html>
<html>
<head>
    <title>Search Engine</title>
    <style>
        body {
            background-image: url('https://images.pexels.com/photos/1809644/pexels-photo-1809644.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'); /* Korrekte Syntax */
            background-size: cover; /* Bild skaliert, um den gesamten Bereich zu füllen */
            background-position: center; /* Bild wird zentriert */
            background-repeat: no-repeat; /* Bild wird nicht wiederholt */
            height: 100vh; /* Stellt sicher, dass der Hintergrund die volle Höhe des Bildschirms einnimmt */
            margin: 0; /* Entfernt den Standardabstand des Browsers */
            overflow: hidden; /* Verhindert, dass es Scrollprobleme gibt */
            font-family: Arial, sans-serif; /* Schriftart einstellen */
            color: white; /* Textfarbe anpassen */
            text-align: center; /* Text wird horizontal zentriert */
            display: flex; /* Flexbox aktiviert */
            justify-content: center; /* Horizontale Zentrierung */
            align-items: center; /* Vertikale Zentrierung */
            flex-direction: column; /* Stellt sicher, dass der Inhalt vertikal gestapelt wird */
        }

        h1 {
            font-size: 70px;
            margin-bottom: 2px; /* Abstand zwischen Titel und Formular */
        }

        form {
            margin-top: 80px; /* Abstand oberhalb des Formulars */
        }

        input[type="text"] {
            padding: 15px;
            width: 600px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        button {
            padding: 10px 20px;
            border: none;
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Search Engine</h1>
    <form action="/search" method="post">
        <input type="text" name="query" placeholder="search term" required>
        <button type="submit">Search</button>
    </form>
</body>
</html>



    """

# Funktion zum Extrahieren des vollständigen Satzes mit dem Suchbegriff 
def extract_sentence(text, query):
    pattern = r'([^.]*?{}[^.]*\.)'.format(re.escape(query)) 
    matches = re.findall(pattern, text, re.IGNORECASE) 
    return matches[0] if matches else "No relevant sentence found."

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
            results_html = f"<h1>Search results for: {query}</h1><ul>"
            for result in results:
                url = result["url"]
                title = result["title"]
                content = result.get("content", "") 
                teaser = extract_sentence(content, query)
                results_html += f'<li><a href="{url}">{title}</a><br>{teaser}</li>'
            results_html += "</ul><a href='/'>back to search</a>"

            return results_html

    except FileNotFoundError as e:
        return f"<h1>Fehler</h1><p>{str(e)}</p><a href='/'>back</a>"
    except Exception as e:
        return f"<h1>Fehler</h1><p>There is an error: {str(e)}</p><a href='/'>back</a>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)