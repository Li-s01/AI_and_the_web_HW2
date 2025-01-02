from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import os

class WebCrawler:
    def __init__(self, start_url, max_pages=50, index_dir="indexdir"):
        self.start_url = start_url
        self.visited = set()
        self.to_visit = [start_url]
        self.max_pages = max_pages
        self.base_domain = urlparse(start_url).netloc

        # Define Whoosh schema
        self.schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)
        self.index = create_in(index_dir, self.schema)

    def crawl(self):
        pages_crawled = 0

        while self.to_visit and pages_crawled < self.max_pages:
            url = self.to_visit.pop(0)

            if url in self.visited:
                continue

            print(f"Crawling: {url}")
            try:
                response = requests.get(url)
                if 'text/html' in response.headers.get('Content-Type', ''):
                    self.visited.add(url)
                    pages_crawled += 1
                    self.index_page(response.text, url)
                else:
                    print(f"Skipping non-HTML content: {url}")
            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")

            time.sleep(1)  # Be polite and avoid overloading the server

        print("Crawling complete.")

    def index_page(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text().lower()
        title = soup.title.string if soup.title else url
        writer = self.index.writer()
        writer.add_document(title=title, path=url, content=text)
        writer.commit()

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if self.is_valid_url(full_url):
                if full_url not in self.visited and full_url not in self.to_visit:
                    self.to_visit.append(full_url)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.base_domain

    def search(self, query):
        from whoosh.qparser import QueryParser
        with self.index.searcher() as searcher:
            parser = QueryParser("content", self.index.schema)
            q = parser.parse(query)
            results = searcher.search(q)
            return [result['path'] for result in results]

if __name__ == "__main__":
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(start_url)
    crawler.crawl()

    # Test search functionality
    search_query = "example page"
    print(f"\nSearch results for '{search_query}': {crawler.search(search_query)}")
