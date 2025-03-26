import os
import pandas as pd
from collections import defaultdict

def getTestFolderNames(path):    
    return [item for item in sorted(os.listdir(path)) if item.startswith('Test') and os.path.isdir(os.path.join(path, item))]

def parse_file(filepath):
    master_name = os.path.basename(filepath).replace("_WindowWiseBW.txt", "")
    master_data = defaultdict(float)
    transaction_counts = defaultdict(lambda: {"READ": 0, "WRITE": 0})
    time_data = defaultdict(lambda: {"Starttime": None, "Endtime": None})
    opcode_counts = defaultdict(lambda: defaultdict(int))
    
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            window, value = parts[0].split('=')
            master_data[window] = float(value)
            
            opcode_value = None
            for part in parts[1:]:
                key, value = part.split('=')
                if key == "Transtype":
                    transaction_counts[window][value] += 1
                elif key == "Opcode":
                    opcode_value = value
                elif key == "Starttime":
                    time_data[window]["Starttime"] = float(value)
                elif key == "Endtime":
                    time_data[window]["Endtime"] = float(value)
            
            if opcode_value:
                opcode_counts[window][opcode_value] += 1
    
    return master_name, master_data, transaction_counts, time_data, opcode_counts

def processTestFolder(directory, test_name):
    master_data = defaultdict(lambda: defaultdict(float))
    transaction_counts = defaultdict(lambda: defaultdict(lambda: {"READ": 0, "WRITE": 0}))
    time_data = defaultdict(lambda: defaultdict(lambda: {"Starttime": None, "Endtime": None}))
    opcode_counts = defaultdict(lambda: defaultdict(int))
    windowwise_time_data = defaultdict(lambda: {"Starttime": None, "Endtime": None})
    total_read_write = defaultdict(lambda: {"READ": 0, "WRITE": 0})
    
    for filename in os.listdir(directory):
        if filename.endswith("WindowWiseBW.txt"):
            filepath = os.path.join(directory, filename)
            master_name, m_data, t_counts, t_data, o_counts = parse_file(filepath)
            
            for window, value in m_data.items():
                master_data[window][master_name] = value
            for window, counts in t_counts.items():
                for key in counts:
                    transaction_counts[master_name][window][key] += counts[key]
                    total_read_write[window][key] += counts[key]
            for window, times in t_data.items():
                if times["Starttime"] is not None and (windowwise_time_data[window]["Starttime"] is None or times["Starttime"] < windowwise_time_data[window]["Starttime"]):
                    windowwise_time_data[window]["Starttime"] = times["Starttime"]
                if times["Endtime"] is not None and (windowwise_time_data[window]["Endtime"] is None or times["Endtime"] > windowwise_time_data[window]["Endtime"]):
                    windowwise_time_data[window]["Endtime"] = times["Endtime"]
                time_data[master_name][window] = times
            for window, opcode_data in o_counts.items():
                for opcode, count in opcode_data.items():
                    opcode_counts[window][opcode] += count
    
    opcode_summary = {window: ", ".join([f"{op}:{count}" for op, count in sorted(opcode_counts[window].items())]) for window in opcode_counts}
    sorted_windowwise_time_data = dict(sorted(windowwise_time_data.items(), key=lambda x: int(x[0].replace("Window", ""))))
    sorted_master_data = dict(sorted(master_data.items(), key=lambda x: int(x[0].replace("Window", ""))))
    sorted_total_read_write = dict(sorted(total_read_write.items(), key=lambda x: int(x[0].replace("Window", ""))))
    sorted_opcode_counts = dict(sorted(opcode_counts.items(), key=lambda x: int(x[0].replace("Window", ""))))
    
    excel_path = os.path.join(directory, f"{test_name}_WindowWiseBW.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        df_main = pd.DataFrame.from_dict(sorted_master_data, orient="index").fillna(0)
        df_totals = pd.DataFrame.from_dict(sorted_total_read_write, orient="index").fillna(0)
        df_opcode = pd.DataFrame.from_dict(opcode_summary, orient="index", columns=["OPCODE"]).fillna("")
        df_time = pd.DataFrame.from_dict(sorted_windowwise_time_data, orient="index").fillna(0)  
        df_main = pd.concat([df_main, df_totals, df_opcode, df_time], axis=1)
        df_main = df_main.sort_index(key=lambda x: x.str.extract(r'(\d+)')[0].astype(int))
        df_main.to_excel(writer, sheet_name="Main")


        for master, window_data in transaction_counts.items():
            df_master = pd.DataFrame.from_dict({
                w: {"READ": d["READ"], "WRITE": d["WRITE"],
                    "Starttime": time_data[master][w]["Starttime"],
                    "Endtime": time_data[master][w]["Endtime"]} 
                for w, d in sorted(window_data.items(), key=lambda x: int(x[0].replace("Window", "")))
            }, orient="index").fillna(0)
            df_master.insert(0, master, df_main[master])
            df_master.to_excel(writer, sheet_name=master, index=True)
    
    print(f"Excel file created: {excel_path}")

def BwDataToExcel():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_folders = getTestFolderNames(base_dir)
    for test_folder in test_folders:
        processTestFolder(os.path.join(base_dir, test_folder), test_folder)

if __name__ == "__main__":
    BwDataToExcel()