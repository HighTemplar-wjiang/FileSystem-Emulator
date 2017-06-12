# FileSystem-Emulator

A file system emulator based on inode structure: https://en.wikipedia.org/wiki/Inode

Enviorment
- python2.6 or above

Run
- python filesystem.py

or
- python2 if default python command is python3
A file named vsf will be created on the real filesystem.

Commands (x and y are parameters)
- quit: quit the emulator
- ls: list directories and files
- check: check bitmap
- cd x: switch to x directory
- open x: open a file named x, create if not exist
- close: close the opened file
- mkdir x: create a directory named x
- write x: write x to the opened file
- read: read opened file
- rm x: remove file x
- rmdir x: remove directory x, files and sub-folders will also be removed
- cp x y: cp x as y
