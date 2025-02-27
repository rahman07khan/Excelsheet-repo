import json
import re
import pandas as pd

# Read the file
with open("alm.txt", "r") as file:
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

# Convert to DataFrame
df_main = pd.DataFrame(requests)

# Checking request_type first, then trans_type
df_F_res_read = df_main[(df_main['master'] == 'F') & (df_main['request_type'] == 'log_axi_performance_monitor') & (df_main['trans_type'] == 'READ')]
df_F_res_write = df_main[(df_main['master'] == 'F') & (df_main['request_type'] == 'log_axi_performance_monitor') & (df_main['trans_type'] == 'WRITE')]
df_F_req_read = df_main[(df_main['master'] == 'F') & (df_main['request_type'] == 'request_handshake') & (df_main['trans_type'] == 'READ')]
df_F_req_write = df_main[(df_main['master'] == 'F') & (df_main['request_type'] == 'request_handshake') & (df_main['trans_type'] == 'WRITE')]

df_G_res_read = df_main[(df_main['master'] == 'G') & (df_main['request_type'] == 'log_axi_performance_monitor') & (df_main['trans_type'] == 'READ')]
df_G_res_write = df_main[(df_main['master'] == 'G') & (df_main['request_type'] == 'log_axi_performance_monitor') & (df_main['trans_type'] == 'WRITE')]
df_G_req_read = df_main[(df_main['master'] == 'G') & (df_main['request_type'] == 'request_handshake') & (df_main['trans_type'] == 'READ')]
df_G_req_write = df_main[(df_main['master'] == 'G') & (df_main['request_type'] == 'request_handshake') & (df_main['trans_type'] == 'WRITE')]


# Creating the 'Main' sheet data
main_data = [
        {"Protocol": "QNM", "Master": "A", "Frequency": "100.345MHz"},
        {"Protocol": "QNM", "Master": "B", "Frequency": "200.456MHz"},
        {"Protocol": "QNM", "Master": "C", "Frequency": "2500.567MHz"},
        {"Protocol": "CHM", "Master": "D", "Frequency": "300.567MHz"},
        {"Protocol": "CHM", "Master": "E", "Frequency": "1023.7655MHz"},
        {"Protocol": "ALM", "Master": "F", "Frequency": "567.0MHz"},
        {"Protocol": "ALM", "Master": "G", "Frequency": "897.0MHz"},
    ]
df_main = pd.DataFrame(main_data)  # Convert to DataFrame

# Save to Excel
excel_filename = "alm_master_data.xlsx"
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    df_main.to_excel(writer, sheet_name="Main", index=False)
    
    df_F_req_write.to_excel(writer, sheet_name="ALM_F_Req_WRITE", index=False)
    df_F_req_read.to_excel(writer, sheet_name="ALM_F_Req_READ", index=False)
    df_F_res_write.to_excel(writer, sheet_name="ALM_F_Res_WRITE", index=False)
    df_F_res_read.to_excel(writer, sheet_name="ALM_F_Res_READ", index=False)

    df_G_req_write.to_excel(writer, sheet_name="ALM_G_Req_WRITE", index=False)
    df_G_req_read.to_excel(writer, sheet_name="ALM_G_Req_READ", index=False)
    df_G_res_write.to_excel(writer, sheet_name="ALM_G_Res_WRITE", index=False)
    df_G_res_read.to_excel(writer, sheet_name="ALM_G_Res_READ", index=False)

print(f"Excel file '{excel_filename}' created successfully with 9 sheets.")
