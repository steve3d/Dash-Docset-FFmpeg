import os, re, shutil, glob, sqlite3
import os.path as path
import urllib.request
from .utils import getDocsetName


class Builder:
    def __init__(self, lib, version):
        self.lib = lib
        self.version = version
        self.cwd = os.getcwd()
        self.buildDir = path.join(self.cwd, 'build')
        self.sourceFile = path.join(self.buildDir, '{}-{}.tar.xz'.format(lib, version))
        self.sourceDir = path.join(self.buildDir, '{}-{}'.format(lib, version))
        self.identifier = getDocsetName(lib)

        if lib == 'ffmpeg':
            self.target = 'doc'
        elif lib == 'libav':
            self.target = 'documentation'
        else:
            raise Exception('Unknown target {}'.format(lib))

        self.docset = '{}.docset'.format(self.identifier)

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

        doxyfile = path.join(self.sourceDir, 'doc/Doxyfile')
        with open(doxyfile) as f:
            contents = f.readlines()
        
        with open(doxyfile, 'w') as f:
            for line in contents:
                line = re.sub(r'^(GENERATE_DOCSET[ ]*=).*$', r'\1 YES', line)
                line = re.sub(r'^(DISABLE_INDEX[ ]*=).*$', r'\1 YES', line)
                line = re.sub(r'^(SEARCHENGINE[ ]*=).*$', r'\1 NO', line)
                line = re.sub(r'^(GENERATE_TREEVIEW[ ]*=).*$', r'\1 NO', line)
                f.write(line)

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
        return

        os.spawnlp(os.P_WAIT, './configure', './configure', '--disable-yasm')
        os.spawnlp(os.P_WAIT, 'make', 'make', 'clean', self.target)
        shutil.rmtree('doc/doxy/html', ignore_errors=True)
        os.spawnlp(os.P_WAIT, 'doxygen', 'doxygen', 'doc/Doxyfile')
        self.copyDocset()
        os.chdir(self.cwd)


        

        
        



