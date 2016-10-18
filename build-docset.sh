#!/bin/bash

SRC="";
URL="";
DOCSET=""
ROOT=`pwd`
IDENTIFIER=''

# macOS and Linux has different behavior of inplace option
if [ `uname` == 'Darwin' ]; then
  SED="sed -i.bak "
else
  SED="sed -i "
fi

function usage {
  echo -e "FFmpeg/Libav Dash Document Generator\n"
  echo -e "Usage:\n\t $0 ffmpeg|libav version\n"
  echo -e "Example: To build ffmpeg 3.0.2 docset:\n \t $0 ffmpeg 3.0.2\n"
}

function prepare {
  # make the build directory
  if [ ! -d build ]; then
      mkdir build
  fi

  if [ $1 == 'ffmpeg' ]; then
    SRC="ffmpeg-$2"
    URL="http://ffmpeg.org/releases/$SRC.tar.xz"
    IDENTIFIER="FFmpeg"
    TARGET="doc"
  elif [ $1 == 'libav' ]; then
    SRC="libav-$2"
    URL="http://libav.org/releases/$SRC.tar.xz"
    IDENTIFIER="Libav"
    TARGET="documentation"
  else
    echo -e "Don't know how to build docset for $1!\n"
    exit 1
  fi

  DOCSET="$IDENTIFIER.docset"

  # download the source
  if [ ! -f "build/$SRC.tar.xz" ]; then
    echo "Downloading $1-$2 source"
    curl -Lo "build/$SRC.tar.xz" $URL
    if [ $? -ne 0 ]; then
       echo "Can not download source."
       rm -rf build/$SRC
       exit 1
    fi
  fi

  if [ ! -d build/$SRC ]; then
  echo "Extracting $SRC source"
  tar Jxf build/$SRC.tar.xz -C build
    if [ $? -ne 0 ]; then
       echo "Can not extract source."
       exit 1
    fi 
  fi

  $SED -e 's/^\(GENERATE_DOCSET[ ]*=\).*$/\1 YES/' build/$SRC/doc/Doxyfile
  $SED -e 's/^\(DISABLE_INDEX[ ]*=\).*$/\1 YES/' build/$SRC/doc/Doxyfile
  $SED -e 's/^\(SEARCHENGINE[ ]*=\).*$/\1 NO/' build/$SRC/doc/Doxyfile
  $SED -e 's/^\(GENERATE_TREEVIEW[ ]*=\).*$/\1 NO/' build/$SRC/doc/Doxyfile
  $SED -e 's/^\(EXCLUDE_SYMBOLS[ ]*\).*$/\1 = AssContext AvsContext CafContext Cell CuvidContext JpeglsContext NuvContext ResampleContext RiceContext segment SoftFloat WebpContext UtVideoContext AACPsyContext /' build/$SRC/doc/Doxyfile
}

function build {
  echo "Building docset..."
  cd $1
  ./configure --disable-yasm && make clean $TARGET
  rm -rf doc/doxy/html && rm -rf $DOCSET && doxygen doc/Doxyfile
  mkdir -p $DOCSET/Contents/Resources/Documents
  cp -rf doc/*.css $DOCSET/Contents/Resources/Documents
  cp -rf doc/*.html $DOCSET/Contents/Resources/Documents
  cp -rf doc/doxy/html $DOCSET/Contents/Resources/Documents/api
  cp -rf $ROOT/icon*.png $DOCSET/
  cp -rf $ROOT/Info.plist $DOCSET/Contents/Info.plist
  $SED -e "s/:IDENTIFIER:/$IDENTIFIER/" $DOCSET/Contents/Info.plist
  $SED -e "s/:NAME:/$NAME/" $DOCSET/Contents/Info.plist
  cd $ROOT
  php build-index.php build/$SRC/$DOCSET $2
}

function package {
  echo "Packaging docset..."
  cd $ROOT
  if [ ! -d $1/$2 ]; then
      mkdir -p $1/$2
  fi

  tar -C build/$SRC --exclude='.DS_Store' \
    --exclude="Info.plist.bak" \
    --exclude="Tokens.xml" \
    --exclude="Nodes.xml" \
    -czf $1/$2/$IDENTIFIER.tgz $DOCSET  
}

# check parameters


if [ -z $2 ]; then
  usage
  exit 0
fi

NAME=$1
VERSION=$2
prepare $NAME $VERSION
build "build/$SRC" $VERSION
package $NAME $VERSION

