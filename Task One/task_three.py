import os
import pandas as pd
import re
from collections import OrderedDict

def parse_log_file(file_path, column_order):
    data = []
    master_name = None
    with open(file_path, 'r') as file:
        for line in file:
            if "[AXI_PERFORMANCE_CHK]:" in line:
                # Extract master name
                master_match = re.search(r'\[Master (\w+)\]', line)
                if master_match:
                    master_name = master_match.group(1)
                
                # Extract key-value pairs
                match = re.match(r'\[AXI_PERFORMANCE_CHK\]:\s*(.*?)\s*=\s*(.*)', line.strip())
                if match:
                    key = re.sub(r'\[Master .*?\]', '', match.group(1).strip()).strip()
                    value = match.group(2).strip()
                    value = 'N/A' if value in ('-nan', '-nanns') else value
                    data.append({"Master": master_name, "Key": key, "Value": value})
                    
                    # Maintain column order
                    if key not in column_order:
                        column_order.append(key)
                else:
                    time_match = re.findall(r'(\b\w+Time\b|active_time) is ([^,]+)', line.strip())
                    if time_match:
                        for key, value in time_match:
                            data.append({"Master": master_name, "Key": key.strip(), "Value": value.strip()})
                            if key not in column_order:
                                column_order.append(key)
    return data

def get_all_txt_files(root_folder):
    txt_files = []
    for folder, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(folder, file))
    return txt_files
# print the channel from left to right 

# def get_channel_data(folder_name):
#     channel_data = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f)) and '_ch' in f]
#     channellist = ""  # Initialize channellist as an empty string
#     for i in range(4):
#         is_okay = False
#         for channelobj in channel_data:
#             num = str(i)
            
#             if num in channelobj:
#                 is_okay = True
#                 channellist += "1" if not channellist else ",1"
#         if not is_okay:
#             channellist += "0" if not channellist else ",0"

#     return channellist

# print the channel from right to left 
def get_channel_data(folder_name):
    channel_data = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f)) and '_ch' in f]
    channellist = "" 
    for i in range(3, -1, -1):  # Iterate from 3 to 0 (Right to Left)
        is_okay = False
        for channelobj in channel_data:
            num = str(i)
            if num in channelobj:
                is_okay = True
                channellist += "1" if not channellist else ",1"
        if not is_okay:
            channellist += "0" if not channellist else ",0"

    return channellist


def get_opcode_data(log_file):
    opcode_counts = {}  # Dictionary to store opcode counts
    with open(log_file, 'r') as file:
        for line in file:
            if "[AXI_PERFORMANCE_CHK]:" not in line:
                opcode_match = re.search(r'trans_type=([^, ]+)', line)
                if opcode_match:
                    opcode_value = opcode_match.group(1)
                    # Increment the count for the opcode
                    opcode_counts[opcode_value] = opcode_counts.get(opcode_value, 0) + 1

    # Format the opcode counts as "OPCODE:COUNT, OPCODE:COUNT"
    opcodedata = ', '.join([f"{opcode}:{count}" for opcode, count in opcode_counts.items()])
    return opcodedata   

from pathlib import Path

# Get the directory where the script is located
base_dir = Path(__file__).resolve().parent

# Ensure the directory exists
if not os.path.exists(base_dir):
    print(f"Error: Directory {base_dir} not found!")
    exit()
# Get all .txt files recursively
log_files = get_all_txt_files(base_dir)

# Parse all log files dynamically maintaining order
all_data = []
column_order = []
already_folderin = []
for log_file in log_files:
    folder_name = os.path.basename(os.path.dirname(log_file))  # Extracts "Test0", "Test1", etc.
    channellist =  get_channel_data(folder_name)
    opcodedata = get_opcode_data(log_file)
    file_data = parse_log_file(log_file, column_order)

    for entry in file_data:
        entry["FolderName"] = folder_name
        entry["FileName"] = os.path.splitext(os.path.basename(log_file))[0]
        entry["Channel"] = channellist
        entry["OPCODE"] = opcodedata
        all_data.append(entry)

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Pivot the DataFrame dynamically following column order
if not df.empty:
    df_pivot = df.pivot_table(index=["FolderName", "FileName", "Master", "Channel", "OPCODE"], 
                              columns="Key", 
                              values="Value", 
                              aggfunc='first').reset_index()
    
    # Ensure columns are in correct order
    ordered_columns = [col for col in ["FolderName", "FileName", "Master","Channel", "OPCODE"] + column_order if col in df_pivot.columns]
    df_pivot = df_pivot[ordered_columns]
    
    # Export to Excel
    excel_output_file = 'each_master.xlsx'
    df_pivot.to_excel(excel_output_file, index=False, sheet_name='AXI_Performance')
    print(f"Processed all log files and saved to {excel_output_file}")
else:
    print("No valid data extracted from log files.")


