import os, os.path as path
import sqlite3, uuid, glob, platform, re
from urllib.parse import quote
import xml.etree.ElementTree as ET
import random, string

class Indexer:
    def __init__(self, lib, version):
        self.cwd = os.getcwd()

        if lib == 'ffmpeg':
            self.target = 'FFmpeg'
        elif lib == 'libav':
            self.target = 'Libav'

        self.docSet = path.join(self.cwd, 'build/{}-{}/{}.docset'.format(lib, version, self.target))
        self.typeDict = {'macro': 'Macro', 'func': 'Function', 'tdef': 'Type', 'econst' :'Enum', 'cl': 'Struct', 'instm' :'Method'}

    def createDatabase(self):
        dbFile = path.join(self.docSet, 'Contents/Resources/docSet.dsidx')
        if path.isfile(dbFile):
            os.unlink(dbFile)

        self.connection = sqlite3.connect(dbFile)
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)')
        self.cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)')

    def buildApi(self):
        tokensFile = path.join(self.docSet, 'Contents/Resources/Documents/api/Tokens.xml')
        path.join(self.docSet, 'Contents/Resources/Documents/api/Tokens.xml')
        self.casePathDict = {}
        self.apiCount = 0
        for event, element in ET.iterparse(tokensFile):
            if event == 'end' and element.tag == 'Token':
                self.processToken(element)
        print('Processed {} Tokens'.format(self.apiCount))
        self.connection.commit()

    def processToken(self, token):
        try:
            ident = token.find('TokenIdentifier')
            tokenType = ident.find('Type').text
            if tokenType in self.typeDict:
                name = ident.find('Name').text
                filePath = token.find('Path').text

                if tokenType == 'cl':
                    b = 1

                if path.isfile(path.join(self.docSet, 'Contents/Resources/Documents/api', filePath)) == False:
                    print("File {} for symbol {} does not exists, skipped".format(filePath, name))
                    return

                lpath = filePath.lower()
                if lpath in self.casePathDict and self.casePathDict[lpath] != filePath:
                    newpath = filePath.replace('.html', '-{}.html'.format(uuid.uuid4()))
                    print("Case conflict, renaming {} to {}".format(filePath, newpath))
                    os.rename(path.join(self.docSet, 'Contents/Resources/Documents/api', filePath),
                        path.join(self.docSet, 'Contents/Resources/Documents/api', newpath))
                    filePath = newpath
                else:
                    self.casePathDict[lpath] = filePath
                
                anchor = token.find('Anchor')
                if anchor != None and anchor.text != '':
                    filePath += '#' + anchor.text

                self.cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)', 
                    (name, self.typeDict[tokenType], 'api/' + filePath))
                self.apiCount += 1
                if self.apiCount % 1000 == 0:
                    print('Processed {} Tokens'.format(self.apiCount))
        except:
            pass
        
    def buildGuides(self):
        for guide in glob.glob(path.join(self.docSet, 'Contents/Resources/Documents/*.html')):
            with open(guide, 'r') as guideFile:
                content = guideFile.read()
            titleRegex = re.compile(r'<h1 class="(titlefont|settitle)">(.*)</h1')
            match = titleRegex.findall(content)
            print('Processing Guide {}'.format(match[0][1]))

            if match and len(match[0]) == 2:
                self.cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)', 
                    (match[0][1], 'Guide', path.basename(guide)))

            sectionRegex = re.compile(r'(<h\d class="\w*"><a href=".*">(.*)</a></h\d>)')

            for sectionMatch in sectionRegex.findall(content):
                s = sectionMatch[0]
                r = s.replace('><a ',
                    '><a class="dashAnchor" name="//apple_ref/Section/{}"></a><a '.format(quote(sectionMatch[1], '')))
                content = content.replace(s, r)

            with open(guide, 'w') as guideFile:
                guideFile.write(content)

        self.connection.commit()

    def testFilesystem(self):
        tempFile = ''.join(random.choices(string.ascii_uppercase, k=8))
        fullPath = path.join(self.cwd, tempFile)
        f = open(fullPath, 'w')
        f.close()
        exists = path.isfile(path.join(self.cwd, tempFile.lower()))
        os.unlink(fullPath)
        
        if exists == True:
            raise Exception('Building FFmpeg/Libav on a case-insensitive is useless.')


    def build(self):
        self.testFilesystem()
        self.createDatabase()
        self.buildApi()
        self.buildGuides()
