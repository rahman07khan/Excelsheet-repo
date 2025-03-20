import os
import pandas as pd
import json

def getTestFolderNames(path):    
    folder_names = []
    for item in sorted(os.listdir(path)):
        if item.startswith('Test'):
            try:
                if os.path.isdir(os.path.join(path, item)):
                    folder_names.append(item)
            except ValueError:               
                continue
    return folder_names

def BwDataToExcel():
    # Load Config File
    with open('config.json', 'r') as file:
        config_content = file.read()
    config_content = config_content.replace('${sim}', os.getenv('sim', 'default_user'))
    config_content = config_content.replace('${unmanaged}', os.getenv('unmanaged', 'default_user'))
    config_content = config_content.replace('${perf_lib}', os.getenv('perf_lib', 'default_user'))
    config = json.loads(config_content)

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    NameOfTestsInTestlist = getTestFolderNames(base_dir)

    all_data = []  # Store all master data for main sheet
    master_names = []

    main_excel_path = os.path.join(base_dir, "Master_WindowWiseBW.xlsx")
    
    with pd.ExcelWriter(main_excel_path, engine='xlsxwriter') as writer:
        for test in NameOfTestsInTestlist:
            directory = os.path.join(base_dir, test)
            data_list = []
            master_names_local = []

            for filename in os.listdir(directory):
                if filename.endswith("WindowWiseBW.txt"):
                    master_name = filename.replace("_WindowWiseBW.txt", "")
                    master_names.append(master_name)
                    master_names_local.append(master_name)

                    with open(os.path.join(directory, filename), 'r') as file:
                        lines = file.readlines()

                    data = {}
                    for line in lines:
                        key, value = line.strip().split('=')
                        data[key] = float(value)

                    data["Master"] = master_name  # Add master name as a column
                    all_data.append(data)  # Store for main sheet
                    data_list.append(data)

            # Create DataFrame for each test's master data
            df_local = pd.DataFrame(data_list)
            df_local.set_index("Master", inplace=True)
            df_local = df_local.T

            # Write each master's data in a separate sheet
            for master in master_names_local:
                df_master = df_local[[master]]
                df_master.to_excel(writer, sheet_name=master, index=True)

        # Create Main Sheet with all master data
        df_main = pd.DataFrame(all_data)
        df_main.set_index("Master", inplace=True)
        df_main = df_main.T
        df_main.to_excel(writer, sheet_name="Main")

    print("Master Excel file created:", main_excel_path)

if __name__ == "__main__":
    BwDataToExcel()
