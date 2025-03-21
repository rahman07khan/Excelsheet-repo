import os
import pandas as pd
import re
from collections import OrderedDict

def parse_log_file(file_path, column_order, opcodemaster=None):
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
    # """ ONLY IF MASTER USED OPCODE DATA"""
    # for masterkey,value in opcodemaster.items():  
    #     data.append({"Master": masterkey, "Key": "OPCODE", "Value": value})
    return data

def get_all_txt_files(root_folder):
    txt_files = []
    for folder, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(folder, file))
    return txt_files

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

# def get_opcode_data(log_file):
#     master_opcode = {}
#     file_name = os.path.splitext(os.path.basename(log_file))[0] 
#     print("file_name",file_name)
#     with open(log_file, 'r') as file:
#         for line in file:
#             if "[AXI_PERFORMANCE_CHK]:" not in line:
#                 master_match = re.search(r'master=([^, ]+)', line)
#                 if master_match:
#                     master_value = master_match.group(1).lower()
#                     master_value = f"{file_name}_{master_value}"
                    
#                     if master_value not in master_opcode:
#                         master_opcode[master_value] = {}
                    
#                     opcode_match = re.search(r'trans_type=([^, ]+)', line)
#                     if opcode_match:
#                         opcode_value = opcode_match.group(1).upper()
#                         master_opcode[master_value][opcode_value] = master_opcode[master_value].get(opcode_value, 0) + 1
    
#     # Format the opcode counts as "OPCODE:COUNT, OPCODE:COUNT"
#     opcodedata = {master: ', '.join([f"{opcode}:{count}" for opcode, count in opcodes.items()]) 
#                   for master, opcodes in master_opcode.items()}
#     return opcodedata   


def get_req_res_urgency(log_file):
    try:
        requrgency_dict = {}  
        resurgency_dict = {}
        with open(log_file, 'r') as file:
            for line in file:
                if "[AXI_PERFORMANCE_CHK]:" not in line and any(keyword in line for keyword in ["log_chi_performance_monitor", "log_qns_performance_monitor", "log_axi_performance_monitor"]):
                    if "log_axi_performance_monitor" in line:
                        arqos_match = re.search(r'arqos=([^, ]+)', line)
                        if arqos_match:
                            arqos_value = arqos_match.group(1)
                            requrgency_dict[arqos_value] = requrgency_dict.get(arqos_value, 0) + 1

                        awqos_match = re.search(r'awqos=([^, ]+)', line) 
                        if awqos_match:
                            awqos_value = awqos_match.group(1)
                            resurgency_dict[awqos_value] = resurgency_dict.get(awqos_value, 0) + 1


                    elif "log_qns_performance_monitor" in line:
                        urgency_match = re.search(r'urgency=([^, ]+)', line)
                        if urgency_match:
                            urgency_value = urgency_match.group(1)
                            requrgency_dict[urgency_value] = requrgency_dict.get(urgency_value, 0) + 1
                    
                        res_urgency_match = re.search(r'Rsp_C_Urgency=([^, ]+)', line)
                        if res_urgency_match:
                            res_urgency_value = res_urgency_match.group(1)
                            resurgency_dict[res_urgency_value] = resurgency_dict.get(res_urgency_value, 0) + 1
                    elif "log_chi_performance_monitor" in line:
                        urgency_match = re.search(r'rEQFLIT_QOS:(\d+)', line)
                        if urgency_match:
                            urgency_value = urgency_match.group(1)
                            requrgency_dict[urgency_value] = requrgency_dict.get(urgency_value, 0) + 1
                        res_urgency_match = re.search(r'rSPFLIT_QOS:(\d+)', line)
                        if res_urgency_match:
                            res_urgency_value = res_urgency_match.group(1)
                            resurgency_dict[res_urgency_value] = resurgency_dict.get(res_urgency_value, 0) + 1
        if len(requrgency_dict) > 0:
            requrgency = ", ".join(f"{key}:{value}" for key, value in requrgency_dict.items())
        else:
            requrgency="N/A"
        if len(resurgency_dict) > 0:
            resurgency = ", ".join(f"{key}:{value}" for key, value in resurgency_dict.items())
        else:
            resurgency="N/A"
        
        return requrgency,resurgency
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERROR",e)

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
    req_urgency,res_urgency = get_req_res_urgency(log_file)
    file_data = parse_log_file(log_file, column_order)

    for entry in file_data:
        entry["FolderName"] = folder_name
        entry["FileName"] = os.path.splitext(os.path.basename(log_file))[0]
        entry["Channel"] = channellist
        entry["OPCODE"] = opcodedata
        entry["Request Urgency"] = req_urgency
        entry["Response Urgency"] = res_urgency
        all_data.append(entry)
# Convert to DataFrame
df = pd.DataFrame(all_data)

# Pivot the DataFrame dynamically following column order
if not df.empty:
    df_pivot = df.pivot_table(index=["FolderName", "FileName", "Master", "Channel", "OPCODE", "Request Urgency", "Response Urgency"], 
                              columns="Key", 
                              values="Value", 
                              aggfunc='first').reset_index()
    
    # Ensure columns are in correct order
    ordered_columns = [col for col in ["FolderName", "FileName", "Master","Channel", "OPCODE", "Request Urgency", "Response Urgency"] + column_order if col in df_pivot.columns]
    df_pivot = df_pivot[ordered_columns]
    
    # Export to Excel
    excel_output_file = 'each_master.xlsx'
    df_pivot.to_excel(excel_output_file, index=False, sheet_name='AXI_Performance')
    print(f"Processed all log files and saved to {excel_output_file}")

# df = pd.DataFrame(all_data)

# # Pivot to reshape the DataFrame
# if not df.empty:
#     df = df.pivot(index=["FolderName", "FileName", "Master", "Channel", "Request Urgency", "Response Urgency"],
#                   columns="Key", 
#                   values="Value").reset_index()

#     # Ensure correct column order
#     ordered_columns = ["FolderName", "FileName", "Master", "Channel", "OPCODE", "Request Urgency", "Response Urgency"]
#     ordered_columns = [col for col in ordered_columns if col in df.columns]

#     # Add remaining columns dynamically
#     all_columns = ordered_columns + [col for col in df.columns if col not in ordered_columns]

#     # Reorder DataFrame
#     df = df[all_columns]


#     # Save to Excel
#     excel_output_file = 'each_master.xlsx'
#     df.to_excel(excel_output_file, index=False, sheet_name='AXI_Performance')
#     print(f"Processed all log files and saved to {excel_output_file}")

else:
    print("No valid data extracted from log files.")


