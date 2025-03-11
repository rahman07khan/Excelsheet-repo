import json
import os
import re
import sys
from Calcinstantaneious_Bw import CalcWindowWiseBW

def get_latest_folder(directory):
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist or is not accessible.")
        return None
    
    entries = os.listdir(directory)
    folders = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
    
    if not folders:
        print(f"No valid folders found in '{directory}'.")
        return None
    
    return max(folders, key=lambda folder: os.path.getmtime(os.path.join(directory, folder)))

def get_matching_files(path):
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return []
    
    # pattern = re.compile(r'^(chm|qnm|alm).*\.txt$')
    
    # for item in os.listdir(path):
    #     if pattern.fullmatch(item) and 'llcc' not in item:
    #         matching_files.append(item)
    

    matching_files = []
    valid_filenames = {"chm.txt", "qnm.txt", "alm.txt"}  # Define exact valid filenames
    
    for item in os.listdir(path):
        if item in valid_filenames:  # Only allow exact filenames
            matching_files.append(item)
    
    return matching_files

def getTestFolderNames(path):
    folder_names = []
    pattern = re.compile(r'^\d+\..*')
    
    for item in sorted(os.listdir(path)):
        if pattern.match(item) and os.path.isdir(os.path.join(path, item)):
            folder_names.append(item)
    
    return folder_names

def CallBandwidthCalculator(Tests, TestDir, MasterList, window):
    for i, test in enumerate(Tests):
        FinalLogDir = os.path.join(TestDir, test, "latest")
        print(f"Processing: {test}, Masters: {MasterList[i]}") 
        CalcWindowWiseBW(MasterList[i], FinalLogDir, window)

# def get_master_data(FinalLogDir):
#     with open(FinalLogDir, "r") as file:
#         data = file.readlines()
#     data_list = []
#     for line in data:
#         master_match = re.search(r'master=([^, ]+)', line)
#         if master_match:
#             master_valueobj = master_match.group(1)
#             master_value = master_valueobj.lower()
#             master_value = f"_{master_value}"

# def get_matching_files(path):
#     if not os.path.exists(path):
#         print(f"Error: Path '{path}' does not exist.")
#         return []
    
#     # pattern = re.compile(r'^(chm|qnm|alm).*\.txt$')
    
#     # for item in os.listdir(path):
#     #     if pattern.fullmatch(item) and 'llcc' not in item:
#     #         matching_files.append(item)
    

#     matching_files = []
#     valid_filenames = {"chm.txt", "qnm.txt", "alm.txt"}  # Define exact valid filenames
    
#     for item in os.listdir(path):
#         full_item_path = os.path.join(path, item)
#         if item in valid_filenames and os.path.isfile(full_item_path):  # Check file existence
#             print("ITEM", item)
#             main_master = item.split('.')[0]
            
#             with open(full_item_path, "r") as file:  # Open using full path
#                 data = file.readlines()
            
#             for line in data:
#                 master_match = re.search(r'master=([^, ]+)', line)
#                 if master_match:
#                     master_name = master_match.group(1).lower()
#                     full_master_mame = f"{main_master}_{master_name}"
                    
#                     if full_master_mame not in matching_files:
#                         print("full_master_mame",full_master_mame)
#                         # master_value = f"{main_master}_{master_match.group(1).lower()}"
#                         matching_files.append(full_master_mame)
    
#     return matching_files

def main():
    try:
        with open('config.json', 'r') as file:
            config_content = file.read()
        
        config_content = config_content.replace('${unmanaged}', os.getenv('unmanaged', 'default_user'))
        config = json.loads(config_content)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        sys.exit(1)
    
    window = int(config.get('Window_Size', 1000))  # Default window size if missing
    TestDir = config.get('Test_Dir', None)
    
    if not TestDir:
        print("Error: 'Test_Dir' not found in config.json.")
        sys.exit(1)
    
    shareID = get_latest_folder(TestDir)
    if not shareID:
        sys.exit(1)
    
    TestDir = os.path.join(TestDir, shareID) #Test_Dir/1741..../
    Tests = getTestFolderNames(TestDir) #0.Test, 1.Test
    
    MasterList = []
    for test in Tests:
        print("TEST",test)
        FinalLogDir = os.path.join(TestDir, test, "latest")
        BwLogList = get_matching_files(FinalLogDir)
        print("BwLogList----",BwLogList)
        Master = [re.match(r'^(.*?)\.txt$', item).group(1) for item in BwLogList if re.match(r'^(.*?)\.txt$', item)]
        MasterList.append(Master)
        print("MasterList---->",MasterList)
    
    CallBandwidthCalculator(Tests, TestDir, MasterList, window)

if __name__ == "__main__":
    main()