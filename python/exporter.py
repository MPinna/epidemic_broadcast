#!/usr/bin/env python

################################################################################
# Exporter program. Converts OMNeT++ simulations result files into .csv files.
################################################################################

import os
import numpy as np

__author__ = 'Marco Pinna, Rambod Rahmani, Yuri Mazzuoli'
__copyright__ = 'Copyright (C) 2021'
__license__ = 'GPLv3'

INPUT_DIR = ""          # change accordingly
OUTPUT_DIR = "csv/"     # change accordingly

SCAVETOOL_PATH = "scavetool" 

CONFIG_NAME = "small"

def getInputFilename(p, r):
    filename = CONFIG_NAME + "-p=" + p + ",R=" + str(r) + "-#" + "*" + ".*"
    return filename

def getOutputFilename(p, r):
    filename = CONFIG_NAME + "-p" + p + "R" + str(r) + ".csv"
    return filename

pValues = np.arange(0.1, 1.0, 0.1)
RValues = np.arange(1.0, 5.0, 0.5)

for p in pValues:
    for r in RValues:
        inputFilename = getInputFilename('%g'%p, ('%f' % r).rstrip('0').rstrip('.'))
        outputFilename = getOutputFilename('%g'%p, ('%f' % r).rstrip('0').rstrip('.'))
        outputPath = OUTPUT_DIR + outputFilename
        inputPath = INPUT_DIR + inputFilename
        command = SCAVETOOL_PATH + " export -o " + outputPath + " -F CSV-R " + inputPath
        print("RUNNING: " + command)
        print("Exporting into " + outputPath)
        os.system(command)
