import os
import pandas as pd
import json
from collections import defaultdict

def getTestFolderNames(path):    
    return [item for item in sorted(os.listdir(path)) if item.startswith('Test') and os.path.isdir(os.path.join(path, item))]

def processTestFolder(directory, test_name):
    master_data = defaultdict(lambda: defaultdict(float))  # Store data for Main Sheet (Window-wise)
    transaction_counts = defaultdict(lambda: defaultdict(lambda: {"READ": 0, "WRITE": 0}))  # Store transaction counts

    for filename in os.listdir(directory):
        if filename.endswith("WindowWiseBW.txt"):
            master_name = filename.replace("_WindowWiseBW.txt", "")

            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()

            for line in lines:
                parts = line.strip().split(',')
                data_dict = {}

                # Extract window name (first part before "=")
                first_pair = parts[0].split('=')
                if len(first_pair) == 2:
                    window = first_pair[0]  # Window name (e.g., Window0)
                    master_data[window][master_name] = float(first_pair[1])  # Store value in Main Sheet format

                # Extract remaining values
                for part in parts[1:]:  
                    key, value = part.split('=')
                    if key == "Transtype":
                        transaction_counts[master_name][window][value] += 1  # Count READ/WRITE

    # Define Excel file path inside the test folder
    excel_path = os.path.join(directory, f"{test_name}_WindowWiseBW.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Create Main Sheet (Windows as rows, Masters as columns) & Sort Windows
        df_main = pd.DataFrame.from_dict(master_data, orient="index").fillna(0)
        df_main = df_main.sort_index(key=lambda x: x.str.extract('(\d+)')[0].astype(int))  # Sort by Window number
        df_main.to_excel(writer, sheet_name="Main")

        # Create Master Sheets (Each master with READ/WRITE counts) & Sort Windows
        for master, window_data in transaction_counts.items():
            df_master = pd.DataFrame.from_dict({w: {"READ": d["READ"], "WRITE": d["WRITE"]} for w, d in window_data.items()}, orient="index").fillna(0)
            df_master.insert(0, master, df_main[master])  # Add master values from Main Sheet
            df_master = df_master.sort_index(key=lambda x: x.str.extract('(\d+)')[0].astype(int))  # Sort by Window number
            
            df_master.to_excel(writer, sheet_name=master, index=True)

    print(f"Excel file created: {excel_path}")

def BwDataToExcel():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    test_folders = getTestFolderNames(base_dir)

    for test_folder in test_folders:
        processTestFolder(os.path.join(base_dir, test_folder), test_folder)

if __name__ == "__main__":
    BwDataToExcel()
