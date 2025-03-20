import os
import re


def createGrepFileExcludeString(LogPath, Intf, tempFile, ExcludedString,master):
    print("createGrepFileExcludeString",LogPath,"tempFile",tempFile)
    """Creates a filtered file with lines containing Intf but excluding ExcludedString."""
    if not os.path.exists(LogPath):
        print(f"Skipping: File '{LogPath}' not found.")
        return
    try:
        masterName = master.split('_')[1].upper()
        with open(LogPath, 'r') as infile, open(tempFile, 'w') as outfile:
            for line in infile:
                if Intf in line and ExcludedString not in line and f'master={masterName}' in line:
                    outfile.write(line)
    except Exception as e:
        print(f"Error creating grep file--------: {e}")

def createGrepFile(LogPath, Intf, tempFile, master):
    """Creates a filtered file with lines containing the specified interface."""
    if not os.path.exists(LogPath):
        print(f"Skipping: File '{LogPath}' not found.")
        return
    try:
        masterName = master.split('_')[1].upper()
        with open(LogPath, 'r') as infile, open(tempFile, 'w') as outfile:
            for line in infile:
                if Intf in line and f'master={masterName}' in line:
                    outfile.write(line)
    except Exception as e:
        print(f"Error creating grep file: {e}")

def CalStartTime(MasterList, LogPath):
    grep_line = "PERFORMANCE_CHK]: overall StartTime is"
    minstarttime_dict = {}
    
    if LogPath.endswith('.txt'):
        FilePath = os.path.dirname(LogPath)  
    else:
        FilePath = LogPath
    TempFilePath = os.path.join(FilePath, "StartTimeTemp.txt")
    
    if not os.path.exists(FilePath):
        print(f"Skipping: File '{FilePath}' not found.")
        return
    
    
    results = {}
    already_line = ""
    try:
        with open(LogPath, 'r') as infile:
            for line in infile:
                if grep_line in line:
                    master_name = already_line.split("[Master ")[1].split("]")[0].strip()
                    results[master_name] = f"{master_name} : {line.strip()}"
                else:
                    already_line = line
        with open(TempFilePath, 'a') as outfile:
            for key, value in results.items():
                outfile.write(value + "\n")
        
        print(f"Filtered data written to '{TempFilePath}'")
    except IOError as io_err:
        print(f"File I/O error: {io_err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    if not os.path.exists(TempFilePath):
        print(f"Skipping: File '{TempFilePath}' not created.")
        return
    try:
        with open(TempFilePath, "r") as filePtr:
            for lines in filePtr:
                MinStartTime = float('inf')
                LineSplit = re.split(r'\s+', lines)
                if len(LineSplit) > 4:
                    StartTime = LineSplit[6].replace("ns", "").replace(",", "").strip()
                    MinStartTime = min(MinStartTime, float(StartTime))
                    mastername = LineSplit[0].split("_")[1].upper()
                    minstarttime_dict[mastername] = MinStartTime
    except ValueError as e:
        print(f"Error parsing StartTime value '{StartTime}': {e}")
    except Exception as e:
        print(f"Error reading StartTimeTemp: {e}")
    return minstarttime_dict


def CalcCHI_BW(FilePath, Intf, tempFile, minstarttime_dict, Window, UpdateFile,master):
    createGrepFileExcludeString(FilePath, Intf, tempFile, "start_time=0.000001",master)
    try:
        with open(tempFile, "r") as filePtr, open(UpdateFile, "w") as filePtr_Write:
            CumlByteCount = 0
            PrevNthWindow = 0
            PrevWindowByteCount = 0
            PrevTransactionByteCount = 0
            
            for line in filePtr:
                start_match = re.search(r"start_time=([\d.e+-]+)", line)
                end_match = re.search(r"end_time=([\d.e+-]+)", line)
                master_match = re.search(r"master=([A-Za-z])", line)
                transtype_match = re.search(r"trans_type=(\w+)", line)
                if not start_match or not end_match:
                    print(f"Skipping line (missing start/end time): {line.strip()}")
                    continue  # Skip invalid lines

                try:
                    StartTime = float(start_match.group(1))
                    EndTime = float(end_match.group(1))
                    master_name = master_match.group(1)
                    transtype = transtype_match.group(1)
                except ValueError:
                    print(f"Skipping line (invalid float conversion): {line.strip()}")
                    continue  # Skip lines where conversion fails
                MinStartTime = minstarttime_dict[master_name]
                Len = 32  # Assuming 32-byte transactions
                CumlByteCount += Len
                SimTime = EndTime - MinStartTime
                NthWindow = int(SimTime / Window)

                if NthWindow != PrevNthWindow:
                    WindowByteCount = PrevTransactionByteCount - PrevWindowByteCount
                    WindowBW = WindowByteCount / Window
                    transtype = "WRITE" if transtype in ["CHI_RSP_OPC_COMP","CHI_REQ_OPC_WRITENOSNPFULL"] else "READ"
                    filePtr_Write.write(f"Window{PrevNthWindow}={WindowBW},Starttime={SimTime},Endtime={EndTime},Transtype={transtype}\n")
                    PrevNthWindow = NthWindow
                    PrevWindowByteCount = PrevTransactionByteCount
                PrevTransactionByteCount = CumlByteCount
    except Exception as e:
        print(f"Error processing CalcCHI_BW: {e}")

def CalcQNS_BW(FilePath, Intf, tempFile, minstarttime_dict, Window, UpdateFile,master):
    createGrepFile(FilePath, Intf, tempFile, master)
    try:
        with open(tempFile, "r") as filePtr, open(UpdateFile, "w") as filePtr_Write:
            CumlByteCount = 0
            PrevNthWindow = 0
            PrevWindowByteCount = 0
            PrevTransactionByteCount = 0
            
            for line in filePtr:
                master_match = re.search(r"master=([A-Za-z])", line)
                transtype_match = re.search(r"trans_type=(\w+)", line)

                master_name = master_match.group(1)
                trans_type = transtype_match.group(1)
                MinStartTime = minstarttime_dict[master_name]
                SplitLines = line.split(",")
                Len = int(SplitLines[8].split("=")[1])
                endtime = float(SplitLines[5].split("=")[1])
                EndTime = endtime/1000
                CumlByteCount += Len
                SimTime = EndTime - MinStartTime
                NthWindow = int(SimTime / Window)
                if NthWindow != PrevNthWindow:
                    WindowByteCount = PrevTransactionByteCount - PrevWindowByteCount
                    WindowBW = WindowByteCount / Window
                    filePtr_Write.write(f"Window{PrevNthWindow}={WindowBW},Starttime={SimTime},Endtime={EndTime},Transtype={trans_type}\n")
                    PrevNthWindow = NthWindow
                    PrevWindowByteCount = PrevTransactionByteCount

                PrevTransactionByteCount = CumlByteCount
    except Exception as e:
        print(f"Error processing CalcQNS_BW: {e}")

def CalcALM_BW(FilePath, Intf, tempFile, minstarttime_dict, Window, UpdateFile,master):
    createGrepFileExcludeString(FilePath, Intf, tempFile, "start_time=0.000001",master)
    try:
        with open(tempFile, "r") as filePtr, open(UpdateFile, "w") as filePtr_Write:
            CumlByteCount = 0
            PrevNthWindow = 0
            PrevWindowByteCount = 0
            PrevTransactionByteCount = 0
            
            for line in filePtr:
                start_match = re.search(r"start_time=([\d.e+-]+)", line)
                end_match = re.search(r"end_time=([\d.e+-]+)", line)
                master_match = re.search(r"master=([A-Za-z])", line)
                transtype_match = re.search(r"trans_type=(\w+)", line)
                if not start_match or not end_match:
                    print(f"Skipping line (missing start/end time): {line.strip()}")
                    continue  # Skip invalid lines

                try:
                    StartTime = float(start_match.group(1))
                    EndTime = float(end_match.group(1))
                    master_name = master_match.group(1)
                    trans_type = transtype_match.group(1)
                except ValueError:
                    print(f"Skipping line (invalid float conversion): {line.strip()}")
                    continue  # Skip lines where conversion fails
                MinStartTime = minstarttime_dict[master_name]
                Len = 32  # Assuming 32-byte transactions
                CumlByteCount += Len
                SimTime = EndTime - MinStartTime
                NthWindow = int(SimTime / Window)

                if NthWindow != PrevNthWindow:
                    WindowByteCount = PrevTransactionByteCount - PrevWindowByteCount
                    WindowBW = WindowByteCount / Window
                    filePtr_Write.write(f"Window{PrevNthWindow}={WindowBW},Starttime={SimTime},Endtime={EndTime},Transtype={trans_type}\n")
                    PrevNthWindow = NthWindow
                    PrevWindowByteCount = PrevTransactionByteCount
                PrevTransactionByteCount = CumlByteCount
    except Exception as e:
        print(f"Error processing CalcCHI_BW: {e}")


def Update_WindowWiseBW(LogPath,MasterList,Window):
    SimulationStartTime = CalStartTime(MasterList, LogPath)
    for master in MasterList:
        if LogPath.endswith('.txt'):
            FilePath = os.path.dirname(LogPath)  
        else:
            FilePath = LogPath
        TempFile = os.path.join(FilePath, f"{master}_TempFile.txt")
        UpdateFile = os.path.join(FilePath, f"{master}_WindowWiseBW.txt")
        if not os.path.exists(FilePath):
            print(f"Skipping {master}: File '{FilePath}' not found.")
            continue

        if not os.path.exists(TempFile):
            open(TempFile, 'a').close()  # Create if missing

        if not os.path.exists(UpdateFile):
            open(UpdateFile, 'a').close()  # Create if missing

        if master.startswith("chm"):
            CalcCHI_BW(LogPath, "log_chi_performance_monitor", TempFile, SimulationStartTime, Window, UpdateFile,master)
        elif master.startswith(("qnm", "qns")):
            CalcQNS_BW(LogPath, "log_qns_performance_monitor", TempFile, SimulationStartTime, Window, UpdateFile,master)
        elif master.startswith("alm"):
            CalcALM_BW(LogPath, "log_axi_performance_monitor", TempFile, SimulationStartTime, Window, UpdateFile,master)
        else:
            print("Please pass correct master name")