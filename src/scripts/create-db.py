import sqlite3

# Nazwa bazy danych
DB_NAME = "chicago_crimes.db"

# Tworzenie tabeli
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS ChicagoCrimes (
        CaseNumber TEXT PRIMARY KEY,
        Date TEXT,
        PrimaryType TEXT,
        Description TEXT,
        LocationDescription TEXT,
        Arrest INTEGER,
        Domestic INTEGER,
        Beat INTEGER,
        District INTEGER,
        Ward INTEGER,
        CommunityArea INTEGER,
        FBICode TEXT,
        Year INTEGER,
        Month INTEGER,
        Day INTEGER,
        Hour INTEGER
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and table created successfully.")
