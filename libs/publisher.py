import os, json, shutil, glob
import os.path as path
from .utils import getDocsetName

class Publisher:
    def __init__(self, lib, version, destdir):
        self.name = getDocsetName(lib)
        self.version = version
        self.docset = self.name + '.tgz'
        self.cwd = os.getcwd()
        self.srcRoot = path.join(self.cwd, 'build', '{}-{}'.format(lib, version))
        self.destDir = path.realpath(destdir)
        self.destRoot = path.join(self.destDir, 'docsets', self.name)

    def getVersion(self):
        ver = dict()
        ver['version'] = self.version
        ver['archive'] = 'versions/{}/{}'.format(self.version, self.docset)
        return ver        

    def updateVersions(self):        
        if path.isfile(path.join(self.destRoot, 'docset.json')):
            with open(path.join(self.destRoot, 'docset.json')) as f:
                versions = json.load(f)
        else: 
            with open(path.join(self.cwd, 'docset.json')) as f:
                versions = json.load(f)

        versions['name'] = self.name
        versions['author']['name'] = 'Steve Yin'
        versions['author']['link'] = 'https://github.com/steve3d/Dash-Docset-FFmpeg'
        
        if len(versions['specific_versions']) == 0:
            versions['version'] = self.version

        if self.version.count('.') == 1:
            minorVersion = self.version
        else:
            minorVersion = self.version[0:self.version.rfind('.')]
        
        filtered = list(filter(lambda x: not x['version'].startswith(minorVersion), versions['specific_versions']))
        filtered.append(self.getVersion())
        filtered.sort(key=lambda x: x['version'], reverse = True)

        versions['specific_versions'] = filtered

        latest = versions['specific_versions'][0]

        if latest['version'] >= versions['version']:
            versions['version'] = latest['version']
            shutil.copy2(path.join(self.srcRoot, self.docset), self.destRoot)
        
        with open(path.join(self.destRoot, 'docset.json'), 'wt') as f:
            f.write(json.dumps(versions, indent = 4))

        self.cleanVersions(versions['specific_versions'])

    def cleanVersions(self, versions):
        existing = list(map(lambda x: x['version'], versions))
        for item in glob.glob(path.join(self.destRoot, 'versions', '*')):        
            ver = item[item.rfind('/') + 1:]
            if ver in existing:
                continue
            else:
                print('Deleting unneeded version: ' + ver)
                shutil.rmtree(item)
    
    def publish(self, dest):
        if not path.isfile(path.join(self.srcRoot, self.docset)):
            print('Docset does not exist, please build it first.')
            return
        
        if not path.isdir(path.join(self.destDir, 'docsets')):
            print('Destination folder is not Dash-User-Contributions repo.')
            return

        versionRoot = path.join(self.destRoot, 'versions', self.version)
        os.makedirs(versionRoot, 0o755, True)
        src = path.join(self.srcRoot, self.docset)
        dest = path.join(versionRoot, self.docset)
        shutil.copy2(path.join(self.srcRoot, self.docset), versionRoot)
        shutil.copy2(path.join(self.cwd, 'icon.png'), self.destRoot)
        shutil.copy2(path.join(self.cwd, 'icon@2x.png'), self.destRoot)
        self.updateVersions()
        print('Publish {}-{} to {} done.'.format(self.name, self.version, self.destDir))