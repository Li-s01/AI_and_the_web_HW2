from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import re
from spellchecker import SpellChecker

app = Flask(__name__)
spell = SpellChecker()

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


# Home page of search engine with search field
@app.route('/')
def index():
    return render_template('temp.html')


# Search route that uses searched word and shows information
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('query').strip()  # searched word input
    else:
        query = request.args.get('query').strip()
   
    try:
        ix = get_index()

        # get suggestions form the spellchecker
        if query not in spell:
            suggestions = spell.candidates(query)
        else:     # makes sure that it isn't an endless loop -> if the word exists, no spelling mistakes = no results and not a new suggestion
            suggestions = []
        
        # Searching index
        with ix.searcher() as searcher:
            query_obj = QueryParser("content", ix.schema).parse(query)
            results = searcher.search(query_obj)
            
            # Prepare results
            search_results = []
            for result in results:
                url = result["url"]
                content = result.get("content", "")
                teaser = extract_sentence(content, query)
                search_results.append({
                    "url": url,
                    "title": result.get("title", url),
                    "teaser": teaser
                })
                
            return render_template('results.html', query=query,  results=search_results, suggestions=suggestions)

    except FileNotFoundError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=f"There is an error: {str(e)}, {query} and object:{query_obj}")


import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
