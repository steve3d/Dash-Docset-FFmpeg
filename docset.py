#!/usr/bin/env python3

import sys, os.path as path
from libs import *
from libs.utils import checkEnv, checkFilesystem

def build(lib, version):
    build = Builder(lib, version)        
    build.build()
    indexer = Indexer(lib, version)
    indexer.build()

def publish(lib, version, dest):
    pub = Publisher(lib, version, dest)
    pub.publish(dest)
    pass

def printHelp():
    print('Usage:')
    printBuildUsage()
    printPublishUsage()
    exit(-1)

def getScriptName():
    return path.basename(sys.argv[0])

def printBuildUsage(header = False):
    if header:
        print('Usage for building:')
    print('\t{} build ffmpeg|libav version'.format(getScriptName()))

def printPublishUsage(header = False):
    if header:
        print('Usage for publish docset:')
    print('\t{} publish ffmpeg|libav version dest'.format(getScriptName()))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        printHelp()

    checkFilesystem()
    if checkEnv() == False:
        print('Please install the missing program.')
        exit(-1)
    
    if sys.argv[1] == 'build':
        if len(sys.argv) != 4:
            printBuildUsage(True)
        else:
            build(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'publish':
        if len(sys.argv) != 5:
            printPublishUsage(True)
        else:
            publish(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        printHelp()

