import json
import re
import pandas as pd
import os

# Define the base directory path dynamically
# base_dir = r"E:\Main Folder\Task One"
from pathlib import Path

# Get the directory where the script is located
base_dir = Path(__file__).resolve().parent

# Ensure the directory exists
if not os.path.exists(base_dir):
    print(f"Error: Directory {base_dir} not found!")
    exit()

# Function to recursively find all .txt files in the directory and subdirectories
def find_txt_files(directory):
    txt_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files
    

# Find all .txt files in the base directory and its subdirectories
txt_files = find_txt_files(base_dir)

if not txt_files:
    print("No .txt files found in the directory or its subdirectories.")
    exit()

# Function to parse CHM-specific data
def parse_chm_file(file_path):
    with open(file_path, "r") as file:
        data = file.readlines()

    data_list = []
    for line in data:
        request_type_match = re.search(r"request_type=(\w+)", line)
        if not request_type_match:
            continue
        
        request_type = request_type_match.group(1)
        json_data = {}

        if request_type == "request_handshake":
            match = re.search(r"<(.*?), Valid req", line)
            if match:
                extracted_info = match.group(1)
                json_data.update(dict(item.split("=") for item in extracted_info.split(", ") if "=" in item))
            
            match = re.search(r"\{start_time:[^}]+, flit:\'\{([^}]*)\}\}", line)
            if match:
                json_data.update(dict(item.split(":") for item in match.group(1).split(", ") if ":" in item))
        else:
            match = re.search(r"<(.*?), and Valid RSPFLIT is", line)
            if match:
                json_data.update(dict(item.split("=") for item in match.group(1).split(", ") if "=" in item))
            
            match = re.search(r"RSPFLIT is \'\{(.*?)\}", line)
            if match:
                json_data.update(dict(item.split(":") for item in match.group(1).split(", ") if ":" in item))

        if json_data:
            data_list.append(json_data)
    
    return data_list

# Function to parse generic text file
def parse_file(file_path):
    with open(file_path, "r") as file:
        data = file.readlines()

    requests = []
    pattern = re.compile(r"<(.*?)>")
    for line in data:
        match = pattern.search(line)
        if match:
            request_dict = {}
            for param in match.group(1).split(", "):
                if "=" in param:
                    key, value = param.split("=")
                    try:
                        request_dict[key] = int(value, 16) if value.startswith("0x") else float(value) if '.' in value else int(value)
                    except ValueError:
                        request_dict[key] = value  # Keep as string if conversion fails
            requests.append(request_dict)
    return requests

# Main reference data
df_main = pd.DataFrame([
    {"Protocol": "QNM", "Master": "A", "Frequency": "100.345MHz"},
    {"Protocol": "QNM", "Master": "B", "Frequency": "200.456MHz"},
    {"Protocol": "QNM", "Master": "C", "Frequency": "2500.567MHz"},
    {"Protocol": "CHM", "Master": "D", "Frequency": "300.567MHz"},
    {"Protocol": "CHM", "Master": "E", "Frequency": "1023.7655MHz"},
    {"Protocol": "ALM", "Master": "F", "Frequency": "567.0MHz"},
    {"Protocol": "ALM", "Master": "G", "Frequency": "897.0MHz"},
])

# Process each .txt file dynamically
for file_path in txt_files:
    file_name = os.path.basename(file_path)
    protocol = file_name.split(".")[0].upper()
    requests = parse_chm_file(file_path) if protocol == "CHM" else parse_file(file_path)

    if not requests:
        print(f"Warning: No valid requests found in {file_name}. Skipping...")
        continue

    sheets_data = {}
    for req_data in requests:
        master = req_data.get('master', 'Unknown')
        trans_type = req_data.get('trans_type', 'Unknown')
        request_type = req_data.get('request_type', 'Unknown')

        # Dynamically generate sheet name based on protocol, master, request_type, and trans_type
        sheet_name = f"{protocol}_{master}_{request_type}_{trans_type}"
        sheet_name = sheet_name[:31]  # Ensure valid Excel sheet name
        sheets_data.setdefault(sheet_name, []).append(req_data)

    # Get subfolder name
    subfolder = os.path.basename(os.path.dirname(file_path))

    # Define the path to the "result" folder inside the subfolder
    result_folder = os.path.join(base_dir, subfolder, "Result")
    
    # Ensure "result" folder exists
    os.makedirs(result_folder, exist_ok=True)

    # Define the full path for the Excel file inside the "result" folder
    excel_filename = os.path.join(result_folder, f"{protocol.lower()}_master_data.xlsx")

    try:
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            df_main.to_excel(writer, sheet_name="Main", index=False)
            for sheet_name, data in sheets_data.items():
                pd.DataFrame(data).to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Success: {excel_filename} created.")
    except Exception as e:
        print(f"Error: Failed to write {excel_filename}. Exception: {e}")

print("Processing complete.")