import libs.build, libs.indexer


if __name__ == '__main__':
    build = libs.build.Builder('ffmpeg', '4.0')
    if build.checkEnv() == False:
        print('Please install corresponding programs.')
        exit(-1)
        
    # build.copyDocset()
    indexer = libs.indexer.Indexer('ffmpeg', '4.0')
    indexer.build()

