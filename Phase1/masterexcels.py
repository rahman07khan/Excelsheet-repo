import json
import re
import pandas as pd

main_data = [
        {"Protocol": "QNM", "Master": "A", "Frequency": "100.345MHz"},
        {"Protocol": "QNM", "Master": "B", "Frequency": "200.456MHz"},
        {"Protocol": "QNM", "Master": "C", "Frequency": "2500.567MHz"},
        {"Protocol": "CHM", "Master": "D", "Frequency": "300.567MHz"},
        {"Protocol": "CHM", "Master": "E", "Frequency": "1023.7655MHz"},
        {"Protocol": "ALM", "Master": "F", "Frequency": "567.0MHz"},
        {"Protocol": "ALM", "Master": "G", "Frequency": "897.0MHz"},
    ]
df_main = pd.DataFrame(main_data)

# Read the file
with open("qnm.txt", "r") as file:
    data = file.readlines()

requests = []

# Regular expression pattern to parse the requests
pattern = re.compile(r"<(.*?)>")

for line in data:
    match = pattern.search(line)
    if match:
        request_str = match.group(1)
        request_dict = {}
        for param in request_str.split(", "):
            key, value = param.split("=")
            try:
                if value.startswith("0x"):  # Convert hex values
                    request_dict[key] = int(value, 16)
                elif '.' in value:  # Convert float values
                    request_dict[key] = float(value)
                else:  # Convert integer values
                    request_dict[key] = int(value)
            except ValueError:
                request_dict[key] = value  # Keep as string if conversion fails
        requests.append(request_dict)

# Write to Excel
qnmsheets_data = {}

# Categorize JSON data into appropriate sheets
for jsondata in requests:
    master = jsondata.get('master')
    trans_type = jsondata.get('trans_type')

    if jsondata.get('request_type') == 'request_handshake':
        qnmsheet_name = f"QNM_{master}_Req_{trans_type}"
    elif jsondata.get('request_type') == 'log_qns_performance_monitor':
        qnmsheet_name = f"QNM_{master}_Res_{trans_type}"
    else:
        continue  # Skip if request_type is unknown

    if qnmsheet_name not in qnmsheets_data:
        qnmsheets_data[qnmsheet_name] = []  # Initialize empty list

    qnmsheets_data[qnmsheet_name].append(jsondata)  # Append row to the correct sheet

# Write to Excel
excel_filename = "qnm_master_data.xlsx"
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    df_main.to_excel(writer, sheet_name="Main", index=False)  # Write main sheet

    # Write each categorized data to its respective sheet
    for sheet_name, data in qnmsheets_data.items():
        df_json = pd.DataFrame(data)  # Convert list of dicts to DataFrame
        df_json.to_excel(writer, sheet_name=sheet_name, index=False)




""" START ALM EXCEL """
with open("alm.txt", "r") as file:
    data = file.readlines()

almrequests = []

# Regular expression pattern to parse the requests
pattern = re.compile(r"<(.*?)>")

for line in data:
    match = pattern.search(line)
    if match:
        request_str = match.group(1)
        request_dict = {}
        for param in request_str.split(", "):
            key, value = param.split("=")
            try:
                if value.startswith("0x"):  # Convert hex values
                    request_dict[key] = int(value, 16)
                elif '.' in value:  # Convert float values
                    request_dict[key] = float(value)
                else:  # Convert integer values
                    request_dict[key] = int(value)
            except ValueError:
                request_dict[key] = value  # Keep as string if conversion fails
        almrequests.append(request_dict)
almsheets_data = {}

for almjsondata in almrequests:
    master = almjsondata.get('master')
    trans_type = almjsondata.get('trans_type')

    if almjsondata.get('request_type') == 'request_handshake':
        almsheet_name = f"ALM_{master}_Req_{trans_type}"
    elif almjsondata.get('request_type') == 'log_axi_performance_monitor':
        almsheet_name = f"ALM_{master}_Res_{trans_type}"
    else:
        continue  # Skip if request_type is unknown

    if almsheet_name not in almsheets_data:
        almsheets_data[almsheet_name] = []  # Initialize empty list

    almsheets_data[almsheet_name].append(almjsondata)  # Append row to the correct sheet

# Write to Excel
excel_filename = "alm_master_dataa.xlsx"
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    df_main.to_excel(writer, sheet_name="Main", index=False)  # Write main sheet

    # Write each categorized data to its respective sheet
    for sheet_name, data in almsheets_data.items():
        df_json = pd.DataFrame(data)  # Convert list of dicts to DataFrame
        df_json.to_excel(writer, sheet_name=sheet_name, index=False)




""" START CHM EXCEL """
with open("chm.txt", "r") as file:
    data = file.readlines()


data_list = []
count = 1
for line in data:
    print(count)
    count+=1
    request_type_match = re.search(r"request_type=(\w+)", line)

    if request_type_match:
        request_type = request_type_match.group(1)

        if request_type == "request_handshake":
            firstmatch = re.search(r"<(.*?), Valid req", line)
            merged_output = ''
            if firstmatch:
                extracted_info = firstmatch.group(1) 
                first_part = extracted_info.replace("=", ":") # Capture the key-value pairs dynamically
                merged_output = first_part+', '

            secontmatch = re.search(r"\{start_time:[^}]+, flit:\'\{([^}]*)\}\}", line)

            if secontmatch:
                second_part = secontmatch.group(0).split(", flit:'{")[0][1:]  # Remove leading '{'
                third_part = secontmatch.group(1)  # Extract second dictionary content (flit details)

                merged_output += second_part + ", " + third_part  # Merge both parts without '{}'
            
            json_data = {}
            for item in merged_output.split(", "):
                key, value = item.split(":")
                json_data[key.strip()] = value.strip()
            data_list.append(json_data)

        else:
            general_match = re.search(r"<(.*?), and Valid RSPFLIT is", line)
            rspflit_match = re.search(r"RSPFLIT is \'\{(.*?)\}", line)
            reqflit_match = re.search(r"REQFLIT is \'\{(.*?)\}", line)

            json_data = {}

            if general_match:
                extracted_info = general_match.group(1)
                for item in extracted_info.split(", "):
                    if "=" in item:
                        key, value = item.split("=")
                        json_data[key.strip()] = value.strip()

            # Extract RSPFLIT fields
            if rspflit_match:
                rspflit_info = rspflit_match.group(1)
                rspflit_dict = {}
                for item in rspflit_info.split(", "):
                    if ":" in item:
                        key, value = item.split(":")
                        rspflit_dict[key.strip()] = value.strip()
                json_data.update(rspflit_dict)

            # Extract REQFLIT fields
            if reqflit_match:
                reqflit_info = reqflit_match.group(1)
                reqflit_dict = {}
                for item in reqflit_info.split(", "):
                    if "{" in item:
                        item = item.split("{")
                    if ":" in item:
                        key, value = item.split(":")
                        reqflit_dict[key.strip()] = value.strip()
                json_data.update(reqflit_dict)
            data_list.append(json_data)
    else:
        print("Request type not found in the line.")

# all_data = json.dumps(data_list, indent=4)
chmsheets_data = {}
for chmjsondata in data_list:
    master = chmjsondata.get('master')
    trans_type = chmjsondata.get('trans_type')
    if chmjsondata.get('request_type') == 'request_handshake':
        chmsheet_name = f"CHM_{master}{trans_type}"
    elif chmjsondata.get('request_type') == 'log_chi_performance_monitor':
        chmsheet_name = f"CHM_{master}{trans_type}"
    else:   
        continue  # Skip if request_type is unknown

    if chmsheet_name not in chmsheets_data:
        chmsheets_data[chmsheet_name] = []  # Initialize empty list

    chmsheets_data[chmsheet_name].append(chmjsondata)  # Append row to the correct sheet

excel_filename = "chm_master_dataa.xlsx"
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    df_main.to_excel(writer, sheet_name="Main", index=False)  # Write main sheet

    # Write each categorized data to its respective sheet
    for sheet_name, data in chmsheets_data.items():
        df_json = pd.DataFrame(data)  # Convert list of dicts to DataFrame
        df_json.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Excel file '{excel_filename}' created successfully with 12 sheets.")
