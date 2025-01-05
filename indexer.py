from whoosh.index import open_dir

# Funktion zur Überprüfung des Index
def verify_index():
    index_dir = "indexdir"
    try:
        ix = open_dir(index_dir)
        with ix.searcher() as searcher:
            print("Im Index gespeicherte Dokumente:")
            for doc in searcher.all_stored_fields():
                print(doc)
    except Exception as e:
        print(f"Fehler beim Öffnen des Index: {e}")

if __name__ == "__main__":
    verify_index()
