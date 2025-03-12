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
    print("createGrepFile---",LogPath,"tempFile------>",tempFile)
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
    MinStartTime = float('inf')

    for master in MasterList:
        if master.startswith("chm"):
            bw_monitor_last_name = "chm.txt"
        elif master.startswith(("qnm", "qns")):
            bw_monitor_last_name = "qnm.txt"
        else:
            continue
        if LogPath.endswith('.txt'):
            FilePath = os.path.dirname(LogPath)  
        else:
            FilePath = LogPath

        # FilePath = os.path.join(LogPath, f"{master}.txt")
        TempFilePath = os.path.join(FilePath, "StartTimeTemp.txt")

        if not os.path.exists(FilePath):
            print(f"Skipping: File '{FilePath}' not found.")
            continue
        
        createGrepFile(LogPath, grep_line, TempFilePath,master)

        if not os.path.exists(TempFilePath):
            print(f"Skipping: File '{TempFilePath}' not created.")
            continue

        try:
            with open(TempFilePath, "r") as filePtr:
                for lines in filePtr:
                    LineSplit = re.split(r'\s+', lines)
                    if len(LineSplit) > 4:
                        StartTime = LineSplit[4].replace("ns", "").replace(",", "").strip()
                        MinStartTime = min(MinStartTime, float(StartTime))
        except ValueError as e:
            print(f"Error parsing StartTime value '{StartTime}': {e}")
        except Exception as e:
            print(f"Error reading StartTimeTemp: {e}")

    return MinStartTime if MinStartTime != float('inf') else 0.0


def CalcCHI_BW(FilePath, Intf, tempFile, MinStartTime, Window, UpdateFile,master):
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

                if not start_match or not end_match:
                    print(f"Skipping line (missing start/end time): {line.strip()}")
                    continue  # Skip invalid lines

                try:
                    StartTime = float(start_match.group(1))
                    EndTime = float(end_match.group(1))
                except ValueError:
                    print(f"Skipping line (invalid float conversion): {line.strip()}")
                    continue  # Skip lines where conversion fails

                Len = 32  # Assuming 32-byte transactions
                CumlByteCount += Len
                SimTime = EndTime - MinStartTime
                NthWindow = int(SimTime / Window)

                if NthWindow != PrevNthWindow:
                    WindowByteCount = PrevTransactionByteCount - PrevWindowByteCount
                    WindowBW = WindowByteCount / Window
                    filePtr_Write.write(f"Window{PrevNthWindow}={WindowBW}\n")
                    PrevNthWindow = NthWindow
                    PrevWindowByteCount = PrevTransactionByteCount
                PrevTransactionByteCount = CumlByteCount
    except Exception as e:
        print(f"Error processing CalcCHI_BW: {e}")

def CalcQNS_BW(FilePath, Intf, tempFile, MinStartTime, Window, UpdateFile,master):
    createGrepFile(FilePath, Intf, tempFile, master)
    try:
        with open(tempFile, "r") as filePtr, open(UpdateFile, "w") as filePtr_Write:
            CumlByteCount = 0
            PrevNthWindow = 0
            PrevWindowByteCount = 0
            PrevTransactionByteCount = 0
            
            for line in filePtr:
                SplitLines = line.split(",")
                Len = int(SplitLines[8].split("=")[1])
                EndTime = float(SplitLines[5].split("=")[1]) / 1000
                CumlByteCount += Len
                SimTime = EndTime - MinStartTime
                NthWindow = int(SimTime / Window)
                if NthWindow != PrevNthWindow:
                    WindowByteCount = PrevTransactionByteCount - PrevWindowByteCount
                    WindowBW = WindowByteCount / Window
                    filePtr_Write.write(f"Window{PrevNthWindow}={WindowBW}\n")
                    PrevNthWindow = NthWindow
                    PrevWindowByteCount = PrevTransactionByteCount

                PrevTransactionByteCount = CumlByteCount
    except Exception as e:
        print(f"Error processing CalcQNS_BW: {e}")


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
            print("Oops! Support is not yet available for AXI master")
        else:
            print("Please pass correct master name")