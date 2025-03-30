# import re
# import os

# def qnm_extract_data(folder_path):
#     all_results = {}
    
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
        
#         if os.path.isfile(file_path):
#             print(f"\nProcessing file: {filename}")
#             result_list = []

#             if "qnm" in filename.lower():
#                 print("Processing QNM file:", filename)
#                 master_name = None
                
#                 with open(file_path, 'r') as file:
#                     for line in file:
#                         if '<request_type=request_handshake' in line:
#                             master_match = re.search(r'master=([^,]+)', line)
#                             master_name = master_match.group(1) if master_match else None
                            
#                             data_dict = {}
                            
#                             # Extract urgency (qos)
#                             urgency_match = re.search(r'urgency=([^,]+)', line)
#                             if urgency_match:
#                                 data_dict["Urgency"] = urgency_match.group(1)
                            
#                             # Extract len (+1)
#                             len_match = re.search(r'len=([^,]+)', line)
#                             if len_match:
#                                 len_value = len_match.group(1)
#                                 try:
#                                     len_value = str(int(len_value) + 1)
#                                 except ValueError:
#                                     pass
#                                 data_dict["Len"] = len_value
                            
#                             # Extract trans_type
#                             trans_type_match = re.search(r'trans_type=([^,]+)', line)
#                             if trans_type_match:
#                                 data_dict["Transtype"] = trans_type_match.group(1)
                            
#                             if master_name:
#                                 data_dict["Master"] = master_name
                            
#                             result_list.append(data_dict)
                
#                 if result_list:
#                     all_results[filename] = result_list
    
#     return all_results

# def alm_extract_data(folder_path):
#     all_results = {}
    
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
        
#         if os.path.isfile(file_path):
#             print(f"\nProcessing file: {filename}")
#             result_list = []

#             if "alm" in filename.lower():
#                 print("Processing ALM file:", filename)
#                 master_name = None
                
#                 with open(file_path, 'r') as file:
#                     for line in file:
#                         if '<request_type=request_handshake' in line:
#                             master_match = re.search(r'master=([^,]+)', line)
#                             master_name = master_match.group(1) if master_match else None
                            
#                             data_dict = {}
                            
#                             # Extract urgency (arqos)
#                             urgency_match = re.search(r'arqos=([^,>\s]+)', line)
#                             if urgency_match:
#                                 data_dict["Urgency"] = urgency_match.group(1)
                            
#                             # Extract len (arlen)
#                             len_match = re.search(r'arlen=([^,>\s]+)', line)
#                             if len_match:
#                                 len_value = len_match.group(1)
#                                 data_dict["Len"] = len_value
                            
#                             # Extract trans_type
#                             trans_type_match = re.search(r'trans_type=([^,]+)', line)
#                             if trans_type_match:
#                                 data_dict["Transtype"] = trans_type_match.group(1)
                            
#                             if master_name:
#                                 data_dict["Master"] = master_name
                            
#                             result_list.append(data_dict)
                
#                 if result_list:
#                     all_results[filename] = result_list
    
#     return all_results

# def chm_extract_data(folder_path):
#     all_results = {}
    
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
        
#         if os.path.isfile(file_path):
#             print(f"\nProcessing file: {filename}")
#             result_list = []

#             if "chm" in filename.lower():
#                 print("Processing CHM file:", filename)
#                 master_name = None
                
#                 with open(file_path, 'r') as file:
#                     for line in file:
#                         if '<request_type=request_handshake' in line:
#                             master_match = re.search(r'master=([^,]+)', line)
#                             master_name = master_match.group(1) if master_match else None
                            
#                             data_dict = {}
                            
#                             # Extract urgency (rEQFLIT_QOS)
#                             urgency_match = re.search(r'rEQFLIT_QOS:\'h([0-9a-fA-F]+)', line)
#                             if urgency_match:
#                                 data_dict["Urgency"] = urgency_match.group(1)
                            
#                             # Extract len (rEQFLIT_SIZE)
#                             len_match = re.search(r'rEQFLIT_SIZE:\'h([0-9a-fA-F]+)', line)
#                             if len_match:
#                                 len_value = len_match.group(1)
#                                 data_dict["Len"] = len_value
                            
#                             # Extract trans_type
#                             trans_type_match = re.search(r'trans_type=([^,]+)', line)
#                             if trans_type_match:
#                                 data_dict["Transtype"] = trans_type_match.group(1)
                            
#                             if master_name:
#                                 data_dict["Master"] = master_name
                            
#                             result_list.append(data_dict)
                
#                 if result_list:
#                     all_results[filename] = result_list
    
#     return all_results

# def qns_extract_data(folder_path):
#     all_results = {}
    
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
        
#         if os.path.isfile(file_path):
#             print(f"\nProcessing file: {filename}")
#             result_list = []

#             if "qns" in filename.lower():
#                 print("Processing QNS file:", filename)
#                 master_name = None
                
#                 with open(file_path, 'r') as file:
#                     for line in file:
#                         if '<request_type=request_handshake' in line:
#                             master_match = re.search(r'master=([^,]+)', line)
#                             master_name = master_match.group(1) if master_match else None
                            
#                             data_dict = {}
                            
#                             # Extract urgency (qos)
#                             urgency_match = re.search(r'urgency=([^,]+)', line)
#                             if urgency_match:
#                                 data_dict["Urgency"] = urgency_match.group(1)
                            
#                             # Extract len (+1)
#                             len_match = re.search(r'len=([^,]+)', line)
#                             if len_match:
#                                 len_value = len_match.group(1)
#                                 try:
#                                     len_value = str(int(len_value) + 1)
#                                 except ValueError:
#                                     pass
#                                 data_dict["Len"] = len_value
                            
#                             # Extract trans_type
#                             trans_type_match = re.search(r'trans_type=([^,]+)', line)
#                             if trans_type_match:
#                                 data_dict["Transtype"] = trans_type_match.group(1)
                            
#                             if master_name:
#                                 data_dict["Master"] = master_name
                            
#                             result_list.append(data_dict)
                
#                 if result_list:
#                     all_results[filename] = result_list
    
#     return all_results

# folder_path = r"E:\Main Folder\Task 5"

# # Process all file types
# qnm_extracted_data = qnm_extract_data(folder_path)
# alm_extracted_data = alm_extract_data(folder_path)
# chm_extracted_data = chm_extract_data(folder_path)
# qns_extracted_data = qns_extract_data(folder_path)

# # Combine all results if needed
# all_extracted_data = {
#     "qnm": qnm_extracted_data,
#     "alm": alm_extracted_data,
#     "chm": chm_extracted_data,
#     "qns": qns_extracted_data
# }

# print("\nFinal combined results:")
# print(all_extracted_data)


import re
import os
from collections import defaultdict

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
                        len_match = re.search(r'arlen=([^,>\s]+)', line)
                        if len_match:
                            data_dict["Len"] = len_match.group(1)
                        
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
                            data_dict["Transtype"] = trans_type_match.group(1)
                        
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

def save_results_to_files(results, output_folder, prefix):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for master_name, entries in results.items():
        # Create a safe filename
        safe_master_name = re.sub(r'[\\/*?:"<>|]', "_", master_name)
        filename = f"{prefix}_{safe_master_name}.txt"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"Master: {master_name}\n")
            f.write("="*50 + "\n")
            
            for i, entry in enumerate(entries, 1):
                f.write(f"Entry {i}:\n")
                f.write(f"  Source: {entry.get('Source', 'N/A')}\n")
                f.write(f"  Urgency: {entry.get('Urgency', 'N/A')}\n")
                f.write(f"  Len: {entry.get('Len', 'N/A')}\n")
                f.write(f"  Transtype: {entry.get('Transtype', 'N/A')}\n")
                f.write("-"*40 + "\n")
            
            f.write(f"\nTotal entries: {len(entries)}\n")

# Main execution
folder_path = r"E:\Main Folder\Task 5"
output_folder = os.path.join(folder_path, "Extracted_Results")

# Process all file types
qnm_results = qnm_extract_data(folder_path)
alm_results = alm_extract_data(folder_path)
chm_results = chm_extract_data(folder_path)
qns_results = qns_extract_data(folder_path)

# Save results to files
save_results_to_files(qnm_results, output_folder, "QNM")
save_results_to_files(alm_results, output_folder, "ALM")
save_results_to_files(chm_results, output_folder, "CHM")
save_results_to_files(qns_results, output_folder, "QNS")

print("\nExtraction complete. Results saved to:", output_folder)