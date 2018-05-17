import os
import os.path as path
import urllib.request
import re
import platform
import shutil
import glob
import sqlite3


class Builder:
    def __init__(self, lib, version):
        self.lib = lib
        self.version = version
        self.cwd = os.getcwd()
        self.buildDir = path.join(self.cwd, 'build')
        self.sourceFile = path.join(self.buildDir, '{}-{}.tar.xz'.format(lib, version))
        self.sourceDir = path.join(self.buildDir, '{}-{}'.format(lib, version))

        if lib == 'ffmpeg':
            self.target = 'doc'
            self.identifier = 'FFmpeg'
        elif lib == 'libav':
            self.target = 'documentation'
            self.identifier = 'Libav'
        else:
            raise Exception('Unknown target {}'.format(lib))

        self.docset = '{}.docset'.format(self.identifier)

    def checkEnv(self):
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

    def download(self):
        if path.isdir(self.buildDir) == False:
            os.mkdir(self.buildDir)

        if path.exists(self.sourceFile):
            return True

        url = "http://{0}.org/releases/{0}-{1}.tar.xz".format(self.lib, self.version)
        
        print('Downloading {}'.format(url))

        try:
            response = urllib.request.urlopen(url)
            srcFile = open(self.sourceFile, 'wb')
            srcFile.write(response.read())
            srcFile.close()
        except:
            print('Can not download.')
            return False

    def prepare(self):
        if path.exists(self.sourceFile) == False:
            if self.download() == False:
                return False

        if path.isdir(self.sourceDir) == False:
            os.chdir(self.buildDir)
            print('Unpacking source file')
            os.spawnlp(os.P_WAIT, 'tar', 'tar', 'Jxf', self.sourceFile)

        if platform.system() == 'Darwin':
            inplace = '-i.bak'
        else:
            inplace = '-i',

        doxyfile = path.join(self.sourceDir, 'doc/Doxyfile')
        os.spawnlp(os.P_WAIT, 'sed', 'sed', inplace, '-e', r's/^\(GENERATE_DOCSET[ ]*=\).*$/\1 YES/', doxyfile)
        os.spawnlp(os.P_WAIT, 'sed', 'sed', inplace, '-e', r's/^\(DISABLE_INDEX[ ]*=\).*$/\1 YES/', doxyfile)
        os.spawnlp(os.P_WAIT, 'sed', 'sed', inplace, '-e', r's/^\(SEARCHENGINE[ ]*=\).*$/\1 NO/', doxyfile)
        os.spawnlp(os.P_WAIT, 'sed', 'sed', inplace, '-e', r's/^\(GENERATE_TREEVIEW[ ]*=\).*$/\1 NO/', doxyfile)

    def copyDocset(self):
        os.chdir(self.sourceDir)
        shutil.rmtree(self.docset, ignore_errors=True)
        docsetRoot = '{}/Contents/Resources/Documents'.format(self.docset)
        os.makedirs(docsetRoot, exist_ok=True)
        for i in glob.glob('doc/*.css') + glob.glob('doc/*.html'):
            shutil.copy(i, docsetRoot)
        shutil.copytree('doc/doxy/html', path.join(docsetRoot, 'api'))
        shutil.copy(path.join(self.cwd, 'icon.png'), self.docset)
        shutil.copy(path.join(self.cwd, 'icon@2x.png'), self.docset)

        with open(path.join(self.cwd, 'Info.plist'), 'rt') as inPlist:
            content = inPlist.read()
            content = content.replace(':IDENTIFIER:', self.identifier)
            content = content.replace(':NAME:', self.identifier)
            with open(path.join(self.docset, 'Contents', 'Info.plist'), 'wt') as outPlist:
                outPlist.write(content)

    def build(self):
        self.prepare()
        os.chdir(self.sourceDir)

        os.spawnlp(os.P_WAIT, './configure', './configure', '--disable-yasm')
        os.spawnlp(os.P_WAIT, 'make', 'make', 'clean', self.target)
        shutil.rmtree('doc/doxy/html', ignore_errors=True)
        os.spawnlp(os.P_WAIT, 'doxygen', 'doxygen', 'doc/Doxyfile')
        self.copyDocset()
        os.chdir(self.cwd)


        

        
        



