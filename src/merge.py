import pandas as pd

def preprocess_and_merge(input_file1, input_file2, output_file):
    try:
        print(f"Wczytywanie pliku: {input_file1}")
        df1 = pd.read_csv(input_file1, on_bad_lines='skip')

        print(f"Wczytywanie pliku: {input_file2}")
        df2 = pd.read_csv(input_file2, on_bad_lines='skip')

        # Łączenie plików
        print("Łączenie danych...")
        df = pd.concat([df1, df2], ignore_index=True)

        # Konwersja kolumny `Date` na datetime
        print("Przetwarzanie danych...")
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

        # usuwanie duplikatów
        df = df.drop_duplicates()

        # Zapisz przetworzone dane do pliku .csv
        print(f"Zapisywanie danych do pliku: {output_file}")
        df.to_csv(output_file, index=False)
        print("Przetwarzanie zakończone pomyślnie.")

        return df

    except Exception as e:
        print(f"Błąd podczas przetwarzania danych: {e}")
        return None


input_csv1 = "../data/raw/Chicago_Crimes_2008_to_2011.csv"
input_csv2 = "../data/raw/Chicago_Crimes_2012_to_2017.csv"
output_csv = "../data/processed/Chicago_Crimes_2008_to_2017.csv"

merged_df = preprocess_and_merge(input_csv1, input_csv2, output_csv)

if merged_df is not None:
    print("Przykładowe dane połączone i przetworzone:")
    print(merged_df.head())
