import json
import re
import pandas as pd

# Read the file
with open("chm.txt", "r") as file:
    data = file.readlines()


data_list = []
for line in data:
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

print(json.dumps(data_list, indent=4))

    # break
    # matches = pattern.findall(line)  
#     print("matches",matches)
#     for match in matches:
#         print("MATCH:", match)
#         if match:
#             print("ENTERRRR")
#             request_str = match.group(1)
#             request_dict = {}
#             for param in request_str.split(", "):
#                 key, value = param.split("=")
#                 value = value.strip("'")  # Remove extra quotes
#                 # Process hex values properly
#                 try:
#                     if value.startswith("0x"):  # Convert hex values
#                         request_dict[key] = int(value, 16)
#                     elif value.startswith("h"):  # Convert 'hXX' hex format
#                         request_dict[key] = int(value[1:], 16)
#                     elif '.' in value:  # Convert float values
#                         request_dict[key] = float(value)
#                     else:  # Convert integer values
#                         request_dict[key] = int(value)
#                 except ValueError:
#                     request_dict[key] = value  # Keep as string if conversion fails

#         # Filter only 'request_handshake' (Requests) and 'log_chi_performance_monitor' (Responses)
#         if request_dict.get("request_type") in ["request_handshake", "log_chi_performance_monitor"]:
#             requests.append(request_dict)
# for data in requests:
#     print(data) 
#     break