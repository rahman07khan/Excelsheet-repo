import os
import pandas as pd
import re
from collections import OrderedDict

def parse_log_file(file_path, column_order, opcodemaster,master_req_res_dict):
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
    # for item in data:
    #     master = item["Master"]
    #     print("master",master)
    for masterkey,value in opcodemaster.items():  
        data.append({"Master": masterkey, "Key": "OPCODE", "Value": value})
    for mastername,valueobj in master_req_res_dict.items():  
        for key,val in valueobj.items():
            req_res_dict = {}
            req_res_dict['Master'] = mastername
            req_res_dict['Key'] = key
            req_res_dict['Value'] = val
            data.append(req_res_dict)
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
    master_opcode = {}
    file_name = os.path.splitext(os.path.basename(log_file))[0] 
    with open(log_file, 'r') as file:
        for line in file:
            if "[AXI_PERFORMANCE_CHK]:" not in line:
                master_match = re.search(r'master=([^, ]+)', line)
                if master_match:
                    master_value = master_match.group(1).lower()
                    master_value = f"{file_name}_{master_value}"
                    
                    if master_value not in master_opcode:
                        master_opcode[master_value] = {}
                    
                    opcode_match = re.search(r'trans_type=([^, ]+)', line)
                    if opcode_match:
                        opcode_value = opcode_match.group(1).upper()
                        master_opcode[master_value][opcode_value] = master_opcode[master_value].get(opcode_value, 0) + 1
    
    # Format the opcode counts as "OPCODE:COUNT, OPCODE:COUNT"
    opcodedata = {master: ', '.join([f"{opcode}:{count}" for opcode, count in opcodes.items()]) 
                  for master, opcodes in master_opcode.items()}
    return opcodedata   


def get_req_res_urgency(log_file):
    try:
        master_req_res_dict= {}
        file_name = os.path.splitext(os.path.basename(log_file))[0] 
        with open(log_file, 'r') as file:
            for line in file:
                if "[AXI_PERFORMANCE_CHK]:" not in line and any(keyword in line for keyword in ["log_chi_performance_monitor", "log_qns_performance_monitor", "log_axi_performance_monitor"]):
                    master_match = re.search(r'master=([^, ]+)', line)
                    if master_match:
                        master_valueobj = master_match.group(1)
                        master_value = master_valueobj.lower()
                        master_value = f"{file_name}_{master_value}"
                        
                        if master_value not in master_req_res_dict:
                            master_req_res_dict[master_value] = {"Request Urgency":{},"Response Urgency":{}}
                            masterkey=master_req_res_dict[master_value]
                        else:
                            masterkey=master_req_res_dict[master_value]


                    if "log_axi_performance_monitor" in line:
                        arqos_match = re.search(r'arqos=([^, ]+)', line)
                        if arqos_match:
                            arqos_value = arqos_match.group(1)
                            masterkey['Request Urgency'][arqos_value] = masterkey['Request Urgency'].get(arqos_value, 0) + 1

                        awqos_match = re.search(r'awqos=([^, ]+)', line) 
                        if awqos_match:
                            awqos_value = awqos_match.group(1)
                            masterkey['Response Urgency'][awqos_value] = masterkey['Response Urgency'].get(awqos_value, 0) + 1
                            # resurgency_dict[awqos_value] = resurgency_dict.get(awqos_value, 0) + 1


                    elif "log_qns_performance_monitor" in line and f"master={master_valueobj}" in line:
                        urgency_match = re.search(r'urgency=([^, ]+)', line)
                        if urgency_match:
                            urgency_value = urgency_match.group(1)
                            masterkey['Request Urgency'][urgency_value] = masterkey['Request Urgency'].get(urgency_value, 0) + 1
                            # requrgency_dict[urgency_value] = requrgency_dict.get(urgency_value, 0) + 1
                    
                        res_urgency_match = re.search(r'Rsp_C_Urgency=([^, ]+)', line)
                        if res_urgency_match:
                            res_urgency_value = res_urgency_match.group(1)
                            masterkey['Response Urgency'][res_urgency_value] = masterkey['Response Urgency'].get(res_urgency_value, 0) + 1
                            # resurgency_dict[res_urgency_value] = resurgency_dict.get(res_urgency_value, 0) + 1
                    elif "log_chi_performance_monitor" in line and f"master={master_valueobj}" in line:
                        urgency_match = re.search(r'rEQFLIT_QOS:(\d+)', line)
                        if urgency_match:
                            urgency_value = urgency_match.group(1)
                            masterkey['Request Urgency'][urgency_value] = masterkey['Request Urgency'].get(urgency_value, 0) + 1
                            # requrgency_dict[urgency_value] = requrgency_dict.get(urgency_value, 0) + 1
                        res_urgency_match = re.search(r'rSPFLIT_QOS:(\d+)', line)
                        if res_urgency_match:
                            res_urgency_value = res_urgency_match.group(1)
                            masterkey['Response Urgency'][res_urgency_value] = masterkey['Response Urgency'].get(res_urgency_value, 0) + 1
                            # resurgency_dict[res_urgency_value] = resurgency_dict.get(res_urgency_value, 0) + 1
                    
                    # master_req_res_dict[master_value]['Request Urgency'] = requrgency_dict
                    # master_req_res_dict[master_value]['Response Urgency'] = resurgency_dict
        for data,value in master_req_res_dict.items():
            if len(value['Request Urgency']) > 0:
                value['Request Urgency'] = ", ".join(f"{key}:{value}" for key, value in value['Request Urgency'].items())
            else:
                value['Request Urgency'] ="N/A"
            if len(value['Response Urgency']) > 0:
                value['Response Urgency'] = ", ".join(f"{key}:{value}" for key, value in value['Response Urgency'].items())
            else:
                value['Response Urgency']="N/A"
        
        return master_req_res_dict
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
    master_req_res_dict = get_req_res_urgency(log_file)
    print("master_req_res_dict",master_req_res_dict)
    # """ ONLY USE MATER USING OPCODE REMOVE NONE """
    file_data = parse_log_file(log_file, column_order,opcodedata,master_req_res_dict)

    for entry in file_data:
        entry["FolderName"] = folder_name
        entry["FileName"] = os.path.splitext(os.path.basename(log_file))[0]
        entry["Channel"] = channellist
        # entry["Request Urgency"] = req_urgency
        # entry["Response Urgency"] = res_urgency
        all_data.append(entry)
# Convert to DataFrame

df = pd.DataFrame(all_data)

# Pivot to reshape the DataFrame
if not df.empty:
    df = df.pivot(index=["FolderName", "FileName", "Master", "Channel"],
                  columns="Key", 
                  values="Value").reset_index()

    # Ensure correct column order
    ordered_columns = ["FolderName", "FileName", "Master", "Channel", "OPCODE", "Request Urgency", "Response Urgency"]
    ordered_columns = [col for col in ordered_columns if col in df.columns]

    # Add remaining columns dynamically
    all_columns = ordered_columns + [col for col in df.columns if col not in ordered_columns]

    # Reorder DataFrame
    df = df[all_columns]


    # Save to Excel
    excel_output_file = 'each_master.xlsx'
    df.to_excel(excel_output_file, index=False, sheet_name='AXI_Performance')
    print(f"Processed all log files and saved to {excel_output_file}")

else:
    print("No valid data extracted from log files.")


