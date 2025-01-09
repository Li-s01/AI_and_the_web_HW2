from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import re
from spellchecker import SpellChecker

app = Flask(__name__)

# checking if index exists
def get_index():
    index_dir = "indexdir"
    if os.path.exists(index_dir):
        return open_dir(index_dir)
    else:
        raise FileNotFoundError("Whoosh-Index not found. Start the crawler first.")

# home page of search engine with search field
@app.route('/')
def index():
    return render_template('temp.html')

# extracting full sentence with searched word 
def extract_sentence(text, query):
    pattern = r'([^.]*?{}[^.]*\.)'.format(re.escape(query))
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Define unwanted initial phrases
    unwanted_phrases = ["Home Page", "Page \d+", "This is Page \d+"]

    # Filter out unwanted repetitive phrases and initial phrases
    filtered_matches = []
    for match in matches:
        filtered_match = match
        for phrase in unwanted_phrases:
            filtered_match = re.sub(r'^\s*' + phrase + r'\s*', '', filtered_match, flags=re.IGNORECASE)  # Removes the unwanted phrase at the beginning
        filtered_matches.append(filtered_match.strip())
    
    return filtered_matches[0] if filtered_matches else "No relevant sentence found."

# suggest query corrections
def suggest_correction(query):
    spell = SpellChecker()
    corrected_words = [spell.correction(word) for word in query.split()]
    corrected_query = ' '.join(corrected_words)
    return corrected_query

# search route that uses searched word and shows information
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')  # searched word input
    corrected_query = suggest_correction(query)
    try:
        ix = get_index()
        # searching index
        with ix.searcher() as searcher:
            query_obj = QueryParser("content", ix.schema).parse(corrected_query)
            results = searcher.search(query_obj)

            # HTML-results
            results_html = f"<h1>Search results for: {query}</h1>"
            if corrected_query != query:
                results_html += f"<p>Did you mean: <a href='/search?query={corrected_query}'>{corrected_query}</a>?</p>"
            results_html += "<ul>"
        
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
