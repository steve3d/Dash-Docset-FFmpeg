# FFmpeg/Libav Docset Generator

This script creates a API docset for FFmpeg/Libav from its documenation.
The docset can be used in the incredibly useful [Dash](https://kapeli.com/dash).
It is submitted also as a [User Contributed docset](https://github.com/Kapeli/Dash-User-Contributions) for Dash.

## Install

Requires `doxygen`, `texi2html`, `Python 3.6.x`
### Install requirements on Ubuntu:
```
sudo apt-get install texi2html doxygen libsdl1.2-dev libsdl2-dev
```


## Build FFmpeg Docset

```
./build-docset.sh which version
```
`which` is the api you want to build only `ffmpeg` and `libav` are valid option.
`version` is the target ffmpeg/libav version.
For example:
- `./docset.py build ffmpeg 3.0.3` to build ffmpeg 3.0.3 api document
- `./docset.py build libav 10.7` to build libav 10.7 api document

This will downloads the ffmpeg source tarball, generates the ffmpeg documentation, creates the docset
and indexes all documenation files.

*NOTE:* Building the api document on a case-insensitive filesystem is useless, because both ffmpeg and libav have muliple same symbols with different cases, so on a case-insensitive filesystem you will only get the last generated document for those symbols.

## Credits

Thanks for [Klaus Badelt](https://github.com/klausbadelt/ffmpeg-docset) for the original idea.
