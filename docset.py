#!/usr/bin/env python3

import sys, os.path as path
import libs.build, libs.indexer

def build(lib, version):
    build = libs.build.Builder('ffmpeg', '4.0')
    if build.checkEnv() == False:
        print('Please install corresponding programs.')
        exit(-1)
        
    build.build()
    indexer = libs.indexer.Indexer('ffmpeg', '4.0')
    indexer.build()

def publish(lib, version, dest):
    pass

def printBuildUsage():
    name = path.basename(sys.argv[0])
    print('\t{} build ffmpeg|libav version'.format(name))

def printPublishUsage():
    name = path.basename(sys.argv[0])
    print('\t{} publish ffmpeg|libav version dest'.format(name))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        printBuildUsage()
        printPublishUsage()
        exit(-1)
    elif sys.argv[1] == 'build':
        if len(sys.argv) != 4:
            print('Usage for building:')
            printBuildUsage()
            exit(-1)
        build(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'publish':
        if len(sys.argv) != 5:
            print('Usage for publish docset:')
            printPublishUsage()
            exit(-1)
        publish(sys.argv[2], sys.argv[3], sys.argv[4])

