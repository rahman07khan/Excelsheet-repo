import os
import pandas as pd
import re

# Base directory containing all test folders
from pathlib import Path

# Get the directory where the script is located
base_dir = Path(__file__).resolve().parent

# Ensure the directory exists
if not os.path.exists(base_dir):
    print(f"Error: Directory {base_dir} not found!")
    exit()

# Switch flag 
create_channel_sheets = True  # Set this to False if you want only the "Main" sheet

def read_text_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

def extract_columns(text):
    pattern = re.compile(r"(\w+) = [\d.]+")
    columns = []
    seen = set()
    
    for match in pattern.finditer(text):
        col_name = match.group(1)
        if col_name.lower() != "frequency" and col_name not in seen:  # Exclude "Frequency"
            columns.append(col_name)
            seen.add(col_name)

    # Extract additional columns
    extra_columns = ["Write Bandwidth", "Read Bandwidth", "WCK:CK ratio calculated", 
                     "DRAM_Monitor Frequency", "CK Frequency", "Final end time"]

    # Capture new columns from the text
    dynamic_columns = [col for col in extra_columns if col in text]
    
    return columns + dynamic_columns

def extract_values(text, channel, rank, columns):
    pattern = re.compile(fr"LP5:CH{channel} CS{rank} (.*?)\n")
    match = pattern.search(text)
    row_data = {"Category": f"R{rank}CH{channel}"}

    if match:
        row_text = match.group(1)
        for col in columns:
            col_pattern = fr"{col} = ([\d.]+)"
            col_match = re.search(col_pattern, row_text)
            row_data[col] = float(col_match.group(1)) if col_match else "N/A"

    # Extract bandwidth values based on channel and rank
    write_pattern = re.search(fr"LP5:CH{channel}_CS{rank} Write Bandwidth observed (\d+) Mbps", text)
    read_pattern = re.search(fr"LP5:CH{channel}_CS{rank} Read Bandwidth observed (\d+) Mbps", text)
    row_data["Write Bandwidth"] = int(write_pattern.group(1)) if write_pattern else "N/A"
    row_data["Read Bandwidth"] = int(read_pattern.group(1)) if read_pattern else "N/A"
    
    # Extract extra parameters
    extra_patterns = {
        "WCK:CK ratio calculated": r"WCK:CK ratio calculated=([\d.]+)",
        "DRAM_Monitor Frequency": r"DRAM_Monitor Frequency = ([\d.]+) MHz",
        "CK Frequency": r"CK Frequency = ([\d.]+) MHz",
        "Final end time": r"Final end time=([\d.]+)"
    }
    for key, extra_pattern in extra_patterns.items():
        extra_match = re.search(extra_pattern, text)
        row_data[key] = float(extra_match.group(1)) if extra_match else "N/A"

    # Ensure "Frequency" is not included in the data
    row_data.pop("Frequency", None)

    return row_data

def get_channeldata(file_name,channel_data,ddr_utilization_values):
    ch_part = file_name.split("_")[1].split(".")[0].upper()
    if ch_part not in channel_data:
        channel_data.update({ch_part:[]})
    if ch_part not in ddr_utilization_values:
        ddr_utilization_values.update({ch_part:"N/A"})

    return channel_data,ddr_utilization_values

def get_dynamic_channels_and_ranks(text):
    # Extract channel and rank from text based on pattern matching
    channels = list(set(re.findall(r"LP5:CH(\d)", text)))
    ranks = list(set(re.findall(r"CS(\d)", text)))
    
    return sorted(channels, key=int), sorted(ranks, key=int)  # Ensure numerical order

# Loop through each test folder (Test0, Test1, Test2, Test3)
for test_folder in os.listdir(base_dir):
    if os.path.isdir(os.path.join(base_dir, test_folder)):
        
        # Initialize data structures for the main sheet and channel sheets
        main_sheet_data = []
        
        # channel_data, ddr_utilization_values = get_channeldata_and_utilization_values()
        channel_data = {}  # CH0, CH1, CH2, CH3
        ddr_utilization_values = {}  # Initialize DDR Utilization values
        
        # Define the path to the "Result" folder inside the current test folder
        result_folder = os.path.join(base_dir, test_folder, "Result")
        
        # Ensure "Result" folder exists
        os.makedirs(result_folder, exist_ok=True)

        # Create Excel writer for this folder
        excel_file_path = os.path.join(result_folder, f"{test_folder}_summary.xlsx")
        excel_writer = pd.ExcelWriter(excel_file_path, engine="xlsxwriter")

        # Loop through all .log files in the folder
        for file_name in os.listdir(os.path.join(base_dir, test_folder)):
            if file_name.lower().startswith("mem_ch") and file_name.lower().endswith(".log"):
                channel_data,ddr_utilization_values = get_channeldata(file_name,channel_data,ddr_utilization_values)
                file_path = os.path.join(base_dir, test_folder, file_name)

                # Read the file content
                data = read_text_file(file_path)

                # Extract columns 
                columns = extract_columns(data)

                # Get channels and ranks 
                channels, ranks = get_dynamic_channels_and_ranks(data)

                # Loop over the channels and ranks to gather data                
                for channel in channels:
                    data_rows = []
                    for rank in ranks:
                        extracted_values = extract_values(data, channel, rank, columns)
                        data_rows.append(extracted_values)
                    
                    # Compute the "BOTH" row
                    both_values = {"Category": "BOTH"}
                    for metric in columns:
                        val1, val2 = data_rows[0].get(metric, "N/A"), data_rows[1].get(metric, "N/A")
                        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                            both_values[metric] = val1 + val2 if "time" not in metric else max(val1, val2)
                        else:
                            both_values[metric] = "N/A"
                    
                    both_values["Write Bandwidth"] = sum(int(row["Write Bandwidth"]) for row in data_rows if row["Write Bandwidth"] != "N/A")
                    both_values["Read Bandwidth"] = sum(int(row["Read Bandwidth"]) for row in data_rows if row["Read Bandwidth"] != "N/A")
                    data_rows.append(both_values)

                    # Collect DDR utilization values for the summary sheet
                    ddr_column_name = "DDR Utilization" if "DDR Utilization" in data_rows[0] else "ddr_utilization"
                    if ddr_column_name in data_rows[0]:
                        ddr_utilization_values[f"CH{channel}"] = data_rows[0].get(ddr_column_name, "N/A") + data_rows[1].get(ddr_column_name, "N/A")
                    else:
                        ddr_utilization_values[f"CH{channel}"] = "N/A"

                    # Append to the main sheet data
                    main_sheet_data.append({
                        "Channel": f"CH{channel}",
                        "DDR Utilization": ddr_utilization_values[f"CH{channel}"],
                        "R0 Read Bandwidth": data_rows[0]["Read Bandwidth"],
                        "R0 Write Bandwidth": data_rows[0]["Write Bandwidth"],
                        "R1 Read Bandwidth": data_rows[1]["Read Bandwidth"],
                        "R1 Write Bandwidth": data_rows[1]["Write Bandwidth"],
                        "R0-R1 Read Bandwidth": data_rows[2]["Read Bandwidth"],
                        "R0-R1 Write Bandwidth": data_rows[2]["Write Bandwidth"],
                        "DRAM Monitor Frequency": data_rows[0].get("DRAM_Monitor Frequency", "N/A"),
                        "WCK:CK Ratio": data_rows[0].get("WCK:CK ratio calculated", "N/A"),
                        "CK Frequency": data_rows[0].get("CK Frequency", "N/A")
                    })

                    # Append to the respective channel sheet data
                    channel_data[f"CH{channel}"].extend(data_rows)

        # Create the main sheet
        df_main = pd.DataFrame(main_sheet_data)
        df_main.to_excel(excel_writer, sheet_name="Main", index=False)

        # Create the channel sheets if enabled
        if create_channel_sheets:
            for channel, data_rows in channel_data.items():
                df_channel = pd.DataFrame(data_rows, columns=["Category"] + columns)
                df_channel.to_excel(excel_writer, sheet_name=channel, index=False)

        # Close and save the Excel file for this folder
        excel_writer.close()
        print(f"Excel file for {test_folder} generated successfully at {excel_file_path}!")
