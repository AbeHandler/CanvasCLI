from collections import defaultdict
import os
import csv


DIR = "3402"
for fileName in os.listdir(DIR):
    if (fileName != ".ipynb_checkpoints" and "processed" not in fileName):
        print("[*] processing " + fileName)

        date = fileName.split("_")[-1].replace(".csv", "")
        
        attendanceCount = defaultdict(int)

        with open(os.path.join(DIR, fileName), 'r') as currentFile:
            if (fileName.split("_")[0] == "participants"):
                csvReader = csv.reader(currentFile)
                next(csvReader)

                for row in csvReader:
                    minutes = row[-2] # total minutes. Canvas makes 2 rows 
                    if (row[1].find("@") != -1): # has an email
                        attendanceCount[row[0]] += int(minutes)

        fn = DIR + "/processed_" + fileName

        with open(fn, "w") as of:
            of.write("name,present,date\n")
            for key, value in sorted(attendanceCount.items()):
                #print(key+": "+str(value))
                # write to file
                present = 1 if (value >= 40) else 0
                key = key.replace("'", "").replace(" (They/Them)", "")
                of.write(key + ", " + str(present) + "," + date + "," + str(value) + "\n")
