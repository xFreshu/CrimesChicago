import pandas as pd


def preprocess_data(input_csv, output_csv):
    """
    Przetwarza dane z pliku CSV i zapisuje wynik w nowym pliku.

    Args:
        input_csv (str): Ścieżka do wejściowego pliku CSV.
        output_csv (str): Ścieżka do wyjściowego pliku CSV.

    Returns:
        pd.DataFrame: Przetworzony DataFrame.
    """
    try:
        print("Loading raw data...")
        # Wczytaj dane
        df = pd.read_csv(input_csv)
        print("Raw data loaded successfully.")

        print("Preprocessing data...")

        # Konwersja kolumny `Date` na format datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

        # Usuwanie wierszy z brakującymi datami
        df = df.dropna(subset=['Date'])

        # Tworzenie nowych kolumn na podstawie daty
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Day'] = df['Date'].dt.day
        df['Hour'] = df['Date'].dt.hour

        # Filtracja zbędnych kolumn
        columns_to_keep = [
            'ID', 'Case Number', 'Date', 'Primary Type', 'Description',
            'Location Description', 'Arrest', 'Domestic', 'Beat',
            'District', 'Ward', 'Community Area', 'FBI Code', 'Latitude',
            'Longitude', 'Year', 'Month', 'Day', 'Hour', 'X Coordinate', 'Y Coordinate',
            'Location'
        ]
        df = df[columns_to_keep]

        # Opcjonalne usuwanie duplikatów
        df = df.drop_duplicates()

        # Zapisz przetworzone dane do pliku
        df.to_csv(output_csv, index=False)
        print(f"Processed data saved to: {output_csv}")

        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None