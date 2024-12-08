import sqlite3

# Nazwa bazy danych
DB_NAME = "chicago_crimes.db"


# Tworzenie tabeli
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_table_query = """
CREATE TABLE IF NOT EXISTS ChicagoCrimes (
    ID INTEGER PRIMARY KEY,
    CaseNumber TEXT,
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
    Latitude REAL,
    Longitude REAL,
    Year INTEGER,
    Month INTEGER,
    Day INTEGER,
    Hour INTEGER,
    XCoordinate REAL,
    YCoordinate REAL,
    Location TEXT
);

    """

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    print("Tabela utworzona pomyślnie.")
