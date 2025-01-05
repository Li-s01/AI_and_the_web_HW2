#Imports
from flask import Flask, request, render_template_string
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# Flask-App erstellen
app = Flask(__name__)

# Whoosh-Index öffnen
index_dir = "indexdir"
ix = open_dir(index_dir)

# HTML-Template für die Suche und Ergebnisse
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Engine</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: url('/static/background.jpg') no-repeat center center fixed;
            background-size: cover;
            color: #fff;
        }
        .container {
            text-align: center;
            background: rgba(0, 0, 0, 0.7);
            padding: 30px;
            border-radius: 10px;
        }
        h1 {
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 300px;
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            background-color: #007BFF;
            color: white;
        }
        button:hover {
            background-color: #0056b3;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li a {
            color: #FFA500;
            text-decoration: none;
        }
        li a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simple Search Engine</h1>
        <form action="/search" method="get">
            <label for="query">Enter search terms:</label><br>
            <input type="text" id="query" name="query" required>
            <button type="submit">Search</button>
        </form>

        {% if results %}
        <h2>Search Results for: "{{ query }}"</h2>
        <ul>
            {% for result in results %}
            <li><a href="{{ result['url'] }}">{{ result['title'] }}</a></li>
            {% endfor %}
        </ul>
        {% elif query %}
        <p>No results found for "{{ query }}".</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = []

    if query:
        with ix.searcher() as searcher:
            qp = QueryParser("content", schema=ix.schema)
            parsed_query = qp.parse(query)
            search_results = searcher.search(parsed_query)

            for result in search_results:
                results.append({
                    "url": result["url"],
                    "title": result["title"]
                })

    return render_template_string(HTML_TEMPLATE, query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)