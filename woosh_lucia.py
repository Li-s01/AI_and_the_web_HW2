from whoosh.index import create_in
from whoosh.fields import *
import requests
from bs4 import BeautifulSoup
import os

schema = Schema(title=TEXT(stored=True), content=TEXT)

# Create an index in the directory indexdr (the directory must already exist!)
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
ix = create_in("indexdir", schema)


# fetch document contents
def get_docs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else 'No Title'
    content = soup.get_text()
    return title, content

#index content
def index_url(url):
    title, content = get_docs(url)
    writer = ix.writer()
    writer.add_document(title = title, content = content)
    writer.commit()


# URLS für die Seiten (ohne uni osna)
# muss glaube anders gemacht werden...
urls = ['https://vm009.rz.uos.de/crawl/index.html', 'https://vm009.rz.uos.de/crawl/page1.html', 'https://vm009.rz.uos.de/crawl/page2.html', 'https://vm009.rz.uos.de/crawl/page3.html', 'https://vm009.rz.uos.de/crawl/page4.html', 'https://vm009.rz.uos.de/crawl/page5.html', 'https://vm009.rz.uos.de/crawl/page6.html', 'https://vm009.rz.uos.de/crawl/page7.html']

for u in urls:
    index_url(u)


# Retrieving data
from whoosh.qparser import QueryParser

def search_ix(query_str):
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query)
        for r in results:
            print(r)

search_ix("last")
