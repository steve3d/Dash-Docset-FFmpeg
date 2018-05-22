import random, string, os, shutil
import os.path as path

def getDocsetName(lib):
    if lib == 'ffmpeg':
        return 'FFmpeg'
    elif lib == 'libav':
        return 'Libav'

    return None

def checkFilesystem():
    tempFile = ''.join(random.choices(string.ascii_uppercase, k=8))
    fullPath = path.join(os.getcwd(), tempFile)
    f = open(fullPath, 'w')
    f.close()
    exists = path.isfile(path.join(os.getcwd(), tempFile.lower()))
    os.unlink(fullPath)
    
    if exists == True:
        print('Building FFmpeg/Libav on a case-insensitive is useless.')

def checkEnv():
    if shutil.which('doxygen') == None:
        print('I need doxygen to create the docset')
        return False

    if shutil.which('texi2html') == None:
        print('I need texi2html to create the docset')
        return False
    
    if shutil.which('sed') == None:
        print('I need seed to create the docset')
        return False

    return True