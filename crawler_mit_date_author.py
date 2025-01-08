import requests
from bs4 import BeautifulSoup
from whoosh.index import open_dir
from whoosh.fields import Schema, TEXT, ID, DATETIME
from datetime import datetime
import os

# Basis-URL for the website
prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix + 'index.html'

# creating index if not already existing, and schema
def create_index():
    index_dir = "indexdir"
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

        schema = Schema(
            url=ID(stored=True, unique=True),  # URL
            title=TEXT(stored=True),           # title
            content=TEXT(stored=True),         # content
            date=DATETIME(stored=True),        # date
            author=TEXT(stored=True)           # author of page
        )
        from whoosh.index import create_in
        create_in(index_dir, schema)
        print(f"Whoosh-Index was created in '{index_dir}'.")
    else:
        print(f"The index '{index_dir}' already exists.")
    return index_dir

# function to crawl and index web pages
def crawl_and_index():
    # make sure the index exists
    index_dir = create_index()
    ix = open_dir(index_dir)

    # Crawler-Logic
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

                        # collect data
                        title = soup.title.string if soup.title else "No Title"
                        content = soup.get_text()
                        date_text = soup.date.string if soup.date else "No Date"
                        author = soup.author.string if soup.author else  "No Author"

                        # turn date_time into a datetime-object 
                        try: 
                            date = datetime.strptime(date_text, "%Y-%m-%d") 
                        except ValueError: 
                            date = datetime.utcnow() # Fallback, if date is not correct

                        # add to the index
                        writer.update_document(
                            url=url,
                            title=title,
                            content=content,
                            date=date,
                            author=author
                        )
                        print(f"Indexed: {url}")

                        # collect links of the pages
                        for link in soup.find_all("a", href=True):
                            href = link["href"]
                            if href.startswith(prefix) and href not in visited:
                                stack.append(href)     # page 4
                            else:
                                stack.append(prefix + href)  # prefix + page 1... (uni site: error: max recursion depth exceeded)
                            
                        visited.add(url) 
                except Exception as e:
                    print(f"Error when calling the URL: {url}: {e}")

if __name__ == "__main__":
    crawl_and_index()