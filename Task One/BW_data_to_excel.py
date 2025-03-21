import os
import pandas as pd
import json
from collections import defaultdict

def getTestFolderNames(path):    
    return [item for item in sorted(os.listdir(path)) if item.startswith('Test') and os.path.isdir(os.path.join(path, item))]

def processTestFolder(directory, test_name):
    master_data = defaultdict(lambda: defaultdict(float))  # Store data for Main Sheet (Window-wise)
    transaction_counts = defaultdict(lambda: defaultdict(lambda: {"READ": 0, "WRITE": 0}))  # Store transaction counts
    total_read_write = defaultdict(lambda: {"READ": 0, "WRITE": 0})  # Store total READ/WRITE per Window
    opcode_counts = defaultdict(lambda: defaultdict(int))  # Store Opcode counts per Window

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
                opcode_value = None
                for part in parts[1:]:  
                    key, value = part.split('=')
                    if key == "Transtype":
                        transaction_counts[master_name][window][value] += 1  # Count READ/WRITE
                    elif key == "Opcode":
                        opcode_value = value  # Capture Opcode value

                # Update opcode count
                if opcode_value:
                    opcode_counts[window][opcode_value] += 1  # Increment opcode occurrence for the window

    # Calculate Total READ and WRITE for each window
    for master, window_data in transaction_counts.items():
        for window, counts in window_data.items():
            total_read_write[window]["READ"] += counts["READ"]
            total_read_write[window]["WRITE"] += counts["WRITE"]

    # Format Opcode counts into a string
    opcode_summary = {window: ", ".join([f"{op}:{count}" for op, count in sorted(opcode_counts[window].items())]) for window in opcode_counts}

    # Define Excel file path inside the test folder
    excel_path = os.path.join(directory, f"{test_name}_WindowWiseBW.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Create Main Sheet (Windows as rows, Masters as columns)
        df_main = pd.DataFrame.from_dict(master_data, orient="index").fillna(0)

        # Convert total_read_write to DataFrame and append at the end
        df_totals = pd.DataFrame.from_dict(total_read_write, orient="index").fillna(0)
        df_opcode = pd.DataFrame.from_dict(opcode_summary, orient="index", columns=["OPCODE"]).fillna("")  # Convert opcode counts

        # Merge all data together
        df_main = pd.concat([df_main, df_totals, df_opcode], axis=1)  # Append READ, WRITE, and OPCODE columns

        # Sort Windows (Ensures Window0, Window1, Window2 order)
        df_main = df_main.sort_index(key=lambda x: x.str.extract(r'(\d+)')[0].astype(int))  
        df_main.to_excel(writer, sheet_name="Main")

        # Create Master Sheets (Each master with READ/WRITE counts) & Sort Windows
        for master, window_data in transaction_counts.items():
            df_master = pd.DataFrame.from_dict({w: {"READ": d["READ"], "WRITE": d["WRITE"]} for w, d in window_data.items()}, orient="index").fillna(0)
            df_master.insert(0, master, df_main[master])  # Add master values from Main Sheet
            df_master = df_master.sort_index(key=lambda x: x.str.extract(r'(\d+)')[0].astype(int))  
            
            df_master.to_excel(writer, sheet_name=master, index=True)

    print(f"Excel file created: {excel_path}")

def BwDataToExcel():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    test_folders = getTestFolderNames(base_dir)

    for test_folder in test_folders:
        processTestFolder(os.path.join(base_dir, test_folder), test_folder)

if __name__ == "__main__":
    BwDataToExcel()
