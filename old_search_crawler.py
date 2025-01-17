import requests
from bs4 import BeautifulSoup


# Basis-URL for the website
prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix + 'index.html'


# Stack (Agenda) initialise: begin with start-url
stack = [start_url]
# Set to save visited urls
visited = set()
# Index (words -> pages)
index = {}

# Crawler-Algorithm
while stack:
    url = stack.pop()  # take the next URL from the list

    # test if the URL was visited before
    if url not in visited:
        try:
            # get the url with requests
            r = requests.get(url)
            if r.status_code == 200:  # only work with succesfull answers
                print(f"Verarbeitete URL: {url}")
                
                # add url to visited sites
                visited.add(url)
                
                # Parse HTML with BeautifuulSoup
                soup = BeautifulSoup(r.content, 'html.parser')

                exclude = ",.?!:;\/'()-[]"         #charaters to exclude

                # extract text and split into words
                words = soup.get_text().split()
                for word in words:
                    # remove unwanted characters from words
                    word = ''.join(char for char in word.lower().strip() if char not in exclude)
                    if word not in index:
                        index[word] = []  # if word doesn't exist, create a new list
                    if url not in index[word]:
                        index[word].append(url)  # add URL for the word
                
            
                 # collect links of the pages
                        for link in soup.find_all("a", href=True):
                            href = link["href"]
                            if href.startswith(prefix) and href not in visited:
                                stack.append(href)     # page 4
                            else:
                                stack.append(prefix + href)  # prefix + page 1... (uni site: error: max recursion depth exceeded)
                            
                        
        except Exception as e:
            print(f"Error when calling the URL {url}: {e}")
    
    

# print created index
print("\nIndex created for:")
for word, urls in index.items():
    print(f"{word}: {urls}")

# search function
def search(index, query):
    query_words = query.lower().split()  # split search query in words
    result_urls = []

    for word in query_words:
        if word in index:
            if not result_urls:
                result_urls = set(index[word])  # start with the URL of the first word
            else:
                result_urls = result_urls.intersection(set(index[word]))  # find intersection of URLs

    return list(result_urls)  # return the found URLs

# Interactive search function in terminal
print("\nTest the search function:")
while True:
    query = input("Enter a search query (or type 'exit' to stop): ")
    if query == "exit":
        break
    results = search(index, query)
    if results:
        print("Found pages:")
        for url in results:
            print(f"- {url}")
    else:
        print("No results found.")


