# Defining the folder path and file names
archive_path = "./data/raw/archive/"
output_path = "./data/processed/"
output_file = "Chicago_Crimes_Merged.csv"

# List all CSV files in the folder
csv_files = [
    "Chicago_Crimes_2001_to_2004.csv",
    "Chicago_Crimes_2005_to_2007.csv",
    "Chicago_Crimes_2008_to_2011.csv",
    "Chicago_Crimes_2012_to_2017.csv",
]

# Read and combine all files
try:
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(archive_path, file)
        df = pd.read_csv(file_path, low_memory=False)  # Read with low_memory to handle large files
        dataframes.append(df)

    # Concatenate all dataframes
    merged_data = pd.concat(dataframes, ignore_index=True)

    # Save to the processed folder
    os.makedirs(output_path, exist_ok=True)
    merged_file_path = os.path.join(output_path, output_file)
    merged_data.to_csv(merged_file_path, index=False)
    merged_file_path
except Exception as e:
    str(e)