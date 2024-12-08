import sqlite3
import pandas as pd

# Nazwa pliku CSV i bazy danych
CSV_FILE = "../../data/processed/Chicago_Crimes_2008_to_2017.csv"
DB_NAME = "chicago_crimes.db"

def load_data():
    print("Wczytywanie danych...")
    conn = sqlite3.connect(DB_NAME)

    # Wczytanie danych z CSV
    df = pd.read_csv(CSV_FILE)

    # Ujednolicenie nazw kolumn
    df.columns = [col.strip().replace(" ", "") for col in df.columns]

    # Usuwanie duplikatów na podstawie kolumny CaseNumber
    df = df.drop_duplicates(subset=["CaseNumber"])

    # Zastąpienie wartości True/False na 1/0 w kolumnach Arrest i Domestic
    df['Arrest'] = df['Arrest'].apply(lambda x: 1 if x else 0)
    df['Domestic'] = df['Domestic'].apply(lambda x: 1 if x else 0)

    # Wstawianie danych do bazy
    df.to_sql('ChicagoCrimes', conn, if_exists='append', index=False)

    conn.close()

if __name__ == "__main__":
    load_data()
    print("Dane wczytane do bazy SQLite.")
