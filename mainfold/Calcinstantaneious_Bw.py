import os
import re
import argparse

def createGrepFile(LogPath, Intf, tempFile):
    """Creates a filtered file with lines containing the specified interface."""
    if not os.path.exists(LogPath):
        print(f"Skipping: File '{LogPath}' not found.")
        return
    try:
        with open(LogPath, 'r') as infile, open(tempFile, 'w') as outfile:
            for line in infile:
                if Intf in line:
                    outfile.write(line)
    except Exception as e:
        print(f"Error creating grep file: {e}")

def createGrepFileExcludeString(LogPath, Intf, tempFile, ExcludedString):
    """Creates a filtered file with lines containing Intf but excluding ExcludedString."""
    if not os.path.exists(LogPath):
        print(f"Skipping: File '{LogPath}' not found.")
        return
    try:
        with open(LogPath, 'r') as infile, open(tempFile, 'w') as outfile:
            for line in infile:
                if Intf in line and ExcludedString not in line:
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

        FilePath = os.path.join(LogPath, f"{master}.txt")
        TempFilePath = os.path.join(LogPath, "StartTimeTemp.txt")

        if not os.path.exists(FilePath):
            print(f"Skipping: File '{FilePath}' not found.")
            continue

        createGrepFile(FilePath, grep_line, TempFilePath)

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

def CalcCHI_BW(FilePath, Intf, tempFile, MinStartTime, Window, UpdateFile):
    createGrepFileExcludeString(FilePath, Intf, tempFile, "start_time=0.000001")
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
                print("NthWindow",NthWindow,"PrevNthWindow",PrevNthWindow, "PrevWindowByteCount",PrevWindowByteCount, "WindowByteCount",WindowByteCount,"CumlByteCount",CumlByteCount)
    except Exception as e:
        print(f"Error processing CalcCHI_BW: {e}")

# def CalcCHI_BW(FilePath,Intf,tempFile,MinStartTime,Window,UpdateFile):
#     ExcludeString = "start_time=0.000001"      ###This is included to make sure, it does not treat 32B responses of same transaction as two different 64B responses
#     createGrepFileExcludeString(FilePath,Intf,tempFile,ExcludeString)
#     #createGrepFile(FilePath,Intf,tempFile)
#     filePtr = open(tempFile,"r")
#     filePtr_Write = open(UpdateFile,"w")
#     CumlByteCount = 0
#     NthWindow = 0
#     PrevNthWindow = 0
#     PrevWindowByteCount = 0
#     PrevTransactionByteCount = 0
#     WindowByteCount = 0


#     k = 0

#     for lines in filePtr.readlines():

#         #SplitLines = lines.split(",")
#         # SplitLines = lines.split("@")

#         ##Length calculation
#         #LenCompSplit = SplitLines[8].split("=")
#         #Len = int(LenCompSplit[1])
#         Len = 32

#         ##EndTime calculation
#         #EndTimeSplit = SplitLines[5].split("=")
#         #EndTime = float(EndTimeSplit[1])/1000
#         start_match = re.search(r"start_time=([\d.e+-]+)", lines)
#         end_match = re.search(r"end_time=([\d.e+-]+)", lines)
#         if not end_match:
#             print("SKIPPING LINE")
#             continue
#         EndTime = float(end_match.group(1)) / 1000
#         # EndTime = float(SplitLines[-1][1:-3])
       
       
        
#         CumlByteCount = CumlByteCount + Len 

#         k = k + 1

#         CumlByteCountFloat = float(CumlByteCount)
#         print("CumlByteCountFloat",CumlByteCountFloat)
#         print("EndTime - MinStartTime",EndTime ," " ,MinStartTime)
#         SimTime = (EndTime - MinStartTime)
#         print("SimTime",SimTime)
#         NthWindow = int(SimTime/Window)
#         print("NthWindow----",NthWindow)
#         print("SimTime/Window",SimTime,"---",Window)
        
#         if(NthWindow != PrevNthWindow):
#             Moved2NextWindow=1
#         else:
#             Moved2NextWindow=0

#         if(NthWindow>PrevNthWindow+1):
#             print("while loop accessed")
        
#         while(NthWindow>PrevNthWindow+1):
            
#             WindowBWTemp = 0.0
#             WriteData = ("Window%0d=%f\n" %(PrevNthWindow,WindowBWTemp))
#             filePtr_Write.write(WriteData)
#             PrevNthWindow = PrevNthWindow + 1
#             print('came here')

#         if(Moved2NextWindow):
#             print("NthWindow = ",NthWindow,"PrevNthWindow = ",PrevNthWindow)
#             WindowByteCount = (PrevTransactionByteCount - PrevWindowByteCount)
#             PrevWindowByteCount = PrevTransactionByteCount
#             WindowBW = WindowByteCount/Window
#             WriteData = ("Window%0d=%f\n" %(PrevNthWindow,WindowBW))
#             filePtr_Write.write(WriteData)
#             PrevNthWindow = PrevNthWindow + 1
#             #print("num of trans:",k)
#             #k=0
           

#         PrevTransactionByteCount = CumlByteCount

#         print(NthWindow,PrevNthWindow, PrevWindowByteCount, WindowByteCount,CumlByteCount)


def CalcQNS_BW(FilePath, Intf, tempFile, MinStartTime, Window, UpdateFile):
    createGrepFile(FilePath, Intf, tempFile)
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

def CalcWindowWiseBW(MasterList, LogPath, Window):
    SimulationStartTime = CalStartTime(MasterList, LogPath)
    print("SimulationStartTime=", SimulationStartTime)

    if not MasterList:
        print("Empty MasterList")
        return

    for master in MasterList:

        FilePath = os.path.join(LogPath, f"{master}.txt")
        TempFile = os.path.join(LogPath, f"{master}_TempFile.txt")
        UpdateFile = os.path.join(LogPath, f"{master}_WindowWiseBW.txt")
        if not os.path.exists(FilePath):
            print(f"Skipping {master}: File '{FilePath}' not found.")
            continue

        if not os.path.exists(TempFile):
            open(TempFile, 'a').close()  # Create if missing

        if not os.path.exists(UpdateFile):
            open(UpdateFile, 'a').close()  # Create if missing

        if master.startswith("chm"):
            CalcCHI_BW(FilePath, "log_chi_performance_monitor", TempFile, SimulationStartTime, Window, UpdateFile)
        elif master.startswith(("qnm", "qns")):
            CalcQNS_BW(FilePath, "log_qns_performance_monitor", TempFile, SimulationStartTime, Window, UpdateFile)
        elif master.startswith("alm"):
            print("Oops! Support is not yet available for AXI master")
        else:
            print("Please pass correct master name")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-LogDir', required=True, help='Provide the Log Directory')
    parser.add_argument('-ClientList', nargs='+', required=True, help='List of clients')
    parser.add_argument('-window', required=True, type=int, help='Window width in ns')
    args = parser.parse_args()
    
    CalcWindowWiseBW(args.ClientList, args.LogDir, args.window)

if __name__ == "__main__":
    main()
