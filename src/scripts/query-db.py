import sqlite3

# Nazwa bazy danych
DB_NAME = "chicago_crimes.db"

def query_database(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    query = "SELECT * FROM ChicagoCrimes LIMIT 10;"  # Przykładowe zapytanie
    results = query_database(query)
    for row in results:
        print(row)
