import re
import os
from collections import defaultdict
import pandas as pd


def qnm_extract_data(folder_path):
    all_results = defaultdict(list)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and "qnm" in filename.lower():
            print(f"\nProcessing QNM file: {filename}")
            
            with open(file_path, 'r') as file:
                for line in file:
                    if '<request_type=request_handshake' in line:
                        master_match = re.search(r'master=([^,]+)', line)
                        if not master_match:
                            continue
                            
                        master_name = master_match.group(1)
                        data_dict = {}
                        
                        # Extract urgency (qos)
                        urgency_match = re.search(r'urgency=([^,]+)', line)
                        if urgency_match:
                            data_dict["Urgency"] = urgency_match.group(1)
                        
                        # Extract len (+1)
                        len_match = re.search(r'len=([^,]+)', line)
                        if len_match:
                            len_value = len_match.group(1)
                            try:
                                len_value = str(int(len_value) + 1)
                            except ValueError:
                                pass
                            data_dict["Len"] = len_value
                        
                        # Extract trans_type
                        trans_type_match = re.search(r'trans_type=([^,]+)', line)
                        if trans_type_match:
                            data_dict["Transtype"] = trans_type_match.group(1)
                        
                        data_dict["Source"] = filename
                        all_results[master_name].append(data_dict)
    
    return all_results

def alm_extract_data(folder_path):
    all_results = defaultdict(list)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and "alm" in filename.lower():
            print(f"\nProcessing ALM file: {filename}")
            
            with open(file_path, 'r') as file:
                for line in file:
                    if '<request_type=request_handshake' in line:
                        master_match = re.search(r'master=([^,]+)', line)
                        if not master_match:
                            continue
                            
                        master_name = master_match.group(1)
                        data_dict = {}
                        
                        # Extract urgency (arqos)
                        urgency_match = re.search(r'arqos=([^,>\s]+)', line)
                        if urgency_match:
                            data_dict["Urgency"] = urgency_match.group(1)
                        
                        # Extract len (arlen)
                        len_match = re.search(r'arsize=([^,>\s]+)', line)
                        if len_match:
                            arbyte_size = len_match.group(1)
                            data_dict["Len"] = str(2 ** len(arbyte_size) )
                        
                        # Extract trans_type
                        trans_type_match = re.search(r'trans_type=([^,]+)', line)
                        if trans_type_match:
                            data_dict["Transtype"] = trans_type_match.group(1)
                        
                        data_dict["Source"] = filename
                        all_results[master_name].append(data_dict)
    
    return all_results

def chm_extract_data(folder_path):
    all_results = defaultdict(list)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and "chm" in filename.lower():
            print(f"\nProcessing CHM file: {filename}")
            
            with open(file_path, 'r') as file:
                for line in file:
                    if '<request_type=request_handshake' in line:
                        master_match = re.search(r'master=([^,]+)', line)
                        if not master_match:
                            continue
                            
                        master_name = master_match.group(1)
                        data_dict = {}
                        
                        # Extract urgency (rEQFLIT_QOS)
                        urgency_match = re.search(r'rEQFLIT_QOS:\'h([0-9a-fA-F]+)', line)
                        if urgency_match:
                            data_dict["Urgency"] = urgency_match.group(1)
                        
                        # Extract len (rEQFLIT_SIZE)
                        len_match = re.search(r'rEQFLIT_SIZE:\'h([0-9a-fA-F]+)', line)
                        if len_match:
                            data_dict["Len"] = len_match.group(1)
                        
                        # Extract trans_type
                        trans_type_match = re.search(r'trans_type=([^,]+)', line)
                        if trans_type_match:
                            transtype =  trans_type_match.group(1)
                            if transtype in ["CHI_RSP_OPC_COMP","CHI_REQ_OPC_WRITENOSNPFULL"]:
                                data_dict["Transtype"] = "WRITE"
                            else:
                                data_dict["Transtype"] = "READ"
                        
                        data_dict["Source"] = filename
                        all_results[master_name].append(data_dict)
    
    return all_results

def qns_extract_data(folder_path):
    all_results = defaultdict(list)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and "qns" in filename.lower():
            print(f"\nProcessing QNS file: {filename}")
            
            with open(file_path, 'r') as file:
                for line in file:
                    if '<request_type=request_handshake' in line:
                        master_match = re.search(r'master=([^,]+)', line)
                        if not master_match:
                            continue
                            
                        master_name = master_match.group(1)
                        data_dict = {}
                        
                        # Extract urgency (qos)
                        urgency_match = re.search(r'urgency=([^,]+)', line)
                        if urgency_match:
                            data_dict["Urgency"] = urgency_match.group(1)
                        
                        # Extract len (+1)
                        len_match = re.search(r'len=([^,]+)', line)
                        if len_match:
                            len_value = len_match.group(1)
                            try:
                                len_value = str(int(len_value) + 1)
                            except ValueError:
                                pass
                            data_dict["Len"] = len_value
                        
                        # Extract trans_type
                        trans_type_match = re.search(r'trans_type=([^,]+)', line)
                        if trans_type_match:
                            data_dict["Transtype"] = trans_type_match.group(1)
                        
                        data_dict["Source"] = filename
                        all_results[master_name].append(data_dict)
    
    return all_results

# def save_results_to_files(results, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     for master_name, entries in results.items():
#         # Create a safe filename
#         safe_master_name = re.sub(r'[\\/*?:"<>|]', "_", master_name)
#         filename = f"{safe_master_name}.txt"
#         filepath = os.path.join(output_folder, filename)
#         urgency_wise_total = {}
#         transtype_dict = {"READ": 0, "WRITE": 0}
    
#         with open(filepath, 'w') as f:
#             for entry in entries:
#                 urgency = entry["Urgency"]
#                 length = entry["Len"]  # Avoid using 'len' as it is a built-in function
#                 transtype = entry["Transtype"]
                
#                 transtype_dict[transtype] += 1
                
#                 if urgency not in urgency_wise_total:
#                     urgency_wise_total[urgency] = {}
                
#                 if length not in urgency_wise_total[urgency]:
#                     urgency_wise_total[urgency][length] = {"READ": 0, "WRITE": 0}
                
#                 urgency_wise_total[urgency][length][transtype] += 1
                
#                 f.write(f"Urgency: {urgency}, Len: {length}, Transtype: {transtype}\n")
#             f.write("Urgency Wise data\n")
#             print("urgency_wise_total",urgency_wise_total,"safe_master_name",safe_master_name)
#             for urgency, length_data in urgency_wise_total.items():
#                 f.write(f"Urgency: {urgency}\n")
#                 for length, val in length_data.items():
#                     f.write(f"Len: {length}, READ: {val['READ']}, WRITE: {val['WRITE']}\n")

# # Main execution
# folder_path = os.path.dirname(os.path.abspath(__file__))
# output_folder = os.path.join(folder_path, "Extracted_Results")

# # Process all file types
# qnm_results = qnm_extract_data(folder_path)
# alm_results = alm_extract_data(folder_path)
# chm_results = chm_extract_data(folder_path)
# qns_results = qns_extract_data(folder_path)

# # Save results to files
# save_results_to_files(qnm_results, output_folder)
# save_results_to_files(alm_results, output_folder)
# save_results_to_files(chm_results, output_folder)
# save_results_to_files(qns_results, output_folder)

# print("\nExtraction complete. Results saved to:", output_folder)



def save_results_to_excel(results, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    excel_path = os.path.join(output_folder, "Extracted_Results.xlsx")
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    
    # Prepare main summary sheet data
    main_data = []
    master_sheets = {}
    
    for master_name, entries in results.items():
        # Create a safe sheet name
        safe_master_name = re.sub(r'[\/*?:"<>|]', "_", master_name)
        urgency_wise_total = {}
        transtype_dict = {"READ": 0, "WRITE": 0}
        
        master_data = []
        
        for entry in entries:
            urgency = entry["Urgency"]
            length = entry["Len"]
            transtype = entry["Transtype"]
            
            transtype_dict[transtype] += 1
            
            if urgency not in urgency_wise_total:
                urgency_wise_total[urgency] = {}
            
            if length not in urgency_wise_total[urgency]:
                urgency_wise_total[urgency][length] = {"READ": 0, "WRITE": 0}
            
            urgency_wise_total[urgency][length][transtype] += 1
            
            master_data.append({"Urgency": urgency, "Len": length, "Transtype": transtype})
        
        # Store master data in a dictionary to be written later
        master_sheets[safe_master_name] = pd.DataFrame(master_data)
        
        # Add data to the main summary sheet
        for urgency, length_data in urgency_wise_total.items():
            for length, val in length_data.items():
                main_data.append({
                    "Master": safe_master_name,
                    "Urgency": urgency,
                    "Len": length,
                    "READ": val['READ'],
                    "WRITE": val['WRITE']
                })
    
    # Save main summary sheet first
    df_main = pd.DataFrame(main_data)
    df_main.to_excel(writer, sheet_name="Main", index=False)
    
    # Save each master sheet
    for sheet_name, df in master_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    writer.close()
    print("Data successfully saved to", excel_path)

# Main execution
folder_path = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(folder_path, "Extracted_Results")

# Process all file types
qnm_results = qnm_extract_data(folder_path)
alm_results = alm_extract_data(folder_path)
chm_results = chm_extract_data(folder_path)
qns_results = qns_extract_data(folder_path)

# Combine all results
all_results = {**qnm_results, **alm_results, **chm_results, **qns_results}

# Save results to an Excel file
save_results_to_excel(all_results, output_folder)

print("\nExtraction complete. Results saved to:", output_folder)