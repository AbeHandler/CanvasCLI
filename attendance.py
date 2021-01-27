from collections import defaultdict
import os
import csv
attendanceCount = defaultdict(int)

DIR = "3402"
for fileName in os.listdir(DIR):
    if (fileName != ".ipynb_checkpoints"):
        with open(os.path.join(DIR, fileName), 'r') as currentFile:
            if (fileName.split("_")[0] == "participants"):
                # attendance file
                # skip header
                csvReader = csv.reader(currentFile)
                #print
                #next(csvReader)
                for row in csvReader:
                    minutes = row[-2] # total minutes. Canvas makes 2 rows 
                    if (row[1].find("@") != -1): # has an email
                        attendanceCount[row[1]] += int(minutes)


    fn = DIR + "/processed_" + fileName

    attendanceFile = open(fn, "w")
    for key, value in sorted(attendanceCount.items()):
        #print(key+": "+str(value))
        # write to file
        if value >= 40: # must attend 40 minues
            attendanceFile.write(key+","+str(value)+"\n")
        else:
            print("skipping", key, value)
    attendanceFile.close()