from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import re
from spellchecker import SpellChecker

app = Flask(__name__)

# Checking if index exists
def get_index():
    index_dir = "indexdir"
    if os.path.exists(index_dir):
        return open_dir(index_dir)
    else:
        raise FileNotFoundError("Whoosh-Index not found. Start the crawler first.")

# Extracting full sentence with searched word
def extract_sentence(text, query):
    pattern = r'([^.]*?{}[^.]*\.)'.format(re.escape(query))
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Define unwanted initial phrases
    unwanted_phrases = ["Home Page", "Page \\d+", "This is Page \\d+"]

    # Filter out unwanted repetitive phrases and initial phrases
    filtered_matches = []
    for match in matches:
        filtered_match = match
        for phrase in unwanted_phrases:
            filtered_match = re.sub(r'^\s*' + phrase + r'\s*', '', filtered_match, flags=re.IGNORECASE)  # Removes the unwanted phrase at the beginning
        filtered_matches.append(filtered_match.strip())
    
    return filtered_matches[0] if filtered_matches else "No relevant sentence found."

# Suggest query corrections
def suggest_correction(query):
    spell = SpellChecker()
    corrected_words = [spell.correction(word) for word in query.split()]
    corrected_query = ' '.join(corrected_words)
    return corrected_query

# Home page of search engine with search field
@app.route('/')
def index():
    return render_template('temp.html')

# Search route that uses searched word and shows information
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')  # searched word input
    else:
        query = request.args.get('query')

    corrected_query = suggest_correction(query)
    try:
        ix = get_index()
        # Searching index
        with ix.searcher() as searcher:
            query_obj = QueryParser("content", ix.schema).parse(corrected_query)
            results = searcher.search(query_obj)

            # Prepare results
            search_results = []
            for result in results:
                url = result["url"]
                content = result.get("content", "")
                teaser = extract_sentence(content, corrected_query)
                search_results.append({
                    "url": url,
                    "title": result.get("title", url),
                    "teaser": teaser
                })
            
            return render_template('results.html', query=query, corrected_query=corrected_query, results=search_results)

    except FileNotFoundError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=f"There is an error: {str(e)}")

import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
