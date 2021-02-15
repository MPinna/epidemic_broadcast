import os

INPUT_DIR = "../epidemic_broadcast/src/results/"  # change accordingly
OUTPUT_DIR = ""   # change accordingly

SCAVETOOL_PATH = "scavetool" 


CONFIG_NAME = "big"

def getInputFilename(p, r):
    filename = CONFIG_NAME + "-p\=" + p + ",R\=" + r + "-#" + "*" + ".sca"
    return filename

def getOutputFilename(p, r):
    filename = CONFIG_NAME + "-p" + p + "R" + r + ".csv"
    return filename

pValues = []
RValues = []

for p in range(1, 11, 1):
    pValues.append(str(float(p)/10))
# print(pValues)

for r in range(1, 2, 1):
    RValues.append(str(r))

for p in pValues:
    for r in RValues:
        inputFilename = getInputFilename(p, r)
        outputFilename = getOutputFilename(p, r)
        outputPath = OUTPUT_DIR + outputFilename
        inputPath = INPUT_DIR + inputFilename
        command = SCAVETOOL_PATH + " export -T s -o " + outputPath + " -F CSV-R " + inputPath
        print("RUNNING: " + command)
        print("Exporting into " + outputPath)
        os.system(command)

