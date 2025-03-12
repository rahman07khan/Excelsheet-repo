
import os
import pandas as pd
import json
import re

def get_latest_folder(directory):    
    entries = os.listdir(directory)      
    folders = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]    
    # latest_folder = max(folders, key=lambda folder: os.path.getmtime(os.path.join(directory, folder)))    
    return folders
    
def getTestFolderNames(path):    
    folder_names = []
    for item in sorted(os.listdir(path)):
        # if pattern.match(item):
        if item.startswith('Test'):
            try:
                # Check if the item is a directory and matches the pattern
                if os.path.isdir(os.path.join(path, item)):
                    folder_names.append(item)
            except ValueError:               
                continue

    return folder_names

def BwDataToExcel():
    # Directory containing the files
    with open ('config.json','r') as file:
        config_content = file.read()
    config_content = config_content.replace('${sim}',os.getenv('sim','default_user'))
    config_content = config_content.replace('${unmanaged}',os.getenv('unmanaged','default_user'))
    config_content = config_content.replace('${perf_lib}',os.getenv('perf_lib','default_user'))
    config = json.loads(config_content)

    TestDir = config.get('Test_Dir')
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    # shareID = get_latest_folder(base_dir)
    # TestDir = TestDir + "/" + shareID

    NameOfTestsInTestlist = getTestFolderNames(base_dir)
    

    data_list = []
    master_names=[]

    for test in NameOfTestsInTestlist:
        data_list_local =[]
        master_names_local=[]
        directory = base_dir + '/' + test
        # Iterate over each file in the directory
        for filename in os.listdir(directory):
            if filename.endswith("WindowWiseBW.txt"):
                    # Extract master name from the filename
                master_name = filename.replace("_WindowWiseBW.txt", "")
                master_names.append(master_name)
                master_names_local.append(master_name)
                    
                with open(os.path.join(directory, filename), 'r') as file:
                    lines = file.readlines()
        
                    # Extract window data
                data = {}
                for line in lines:
                    key, value = line.strip().split('=')
                    data[key] = float(value)
        
                    
                data_list.append(data)
                data_list_local.append(data)

        # Following is local xlsx for each test
        df_local = pd.DataFrame(data_list_local)
        df_local = df_local[sorted(df_local.columns, key=lambda x: int(x.replace('Window', '')))]
        df_local.index = master_names_local
        df_local = df_local.T
        df_local.to_excel(directory+"/"+test+"_WindowWiseBW.xlsx", index=True, header=True)
        print("Data has been written to:",directory+"/"+test+"_WindowWiseBW.xlsx")
        

if __name__ == "__main__":
    BwDataToExcel()
