import sys
import os


class FileSystem():
    BLOCK_SIZE  = 512
    BLOCK_NUM   = 1000

    INODE_MAP   = [x for x in range(0, 80 // 8)]
    INODE_BLOCK = [x for x in range(1, 81)]

    def __init__(self):
        fspath = os.getcwd() + '/' + "vsf"
        if False == os.path.exists(fspath):
            print("Info: file system does not exist, rebuid")
            self.fs = open("vsf", "w+")

            initData = (chr(0x80) + chr(0x00) * self.INODE_MAP[-1] + #iNode bitmap
                chr(0x80) + chr(0x00) * (self.BLOCK_SIZE - len(self.INODE_MAP) - 1) +  #data bitmap
                'D' + chr(0x00) + chr(len(self.INODE_BLOCK) + 1) + chr(0x00) * (self.BLOCK_SIZE - 3) + #iNode for "/"
                chr(0x00) * self.BLOCK_SIZE * (len(self.INODE_BLOCK) - 1) + #other inodes
                chr(0x00) * self.BLOCK_SIZE * (self.BLOCK_NUM - len(self.INODE_BLOCK) - 1) #data blocks
                )
            self.fs.write(initData)
            self.fs.close()

        else:
            print("Info: file system exists, load")

        self.data = []
        self.__load()
        self.dataStart = self.BLOCK_SIZE * (len(self.INODE_BLOCK) + 1)
        self.curDir = "/"
        self.curInode = self.__getInode(0)


    def __del__(self):
        self.__save()
        self.fs.close()


    def __load(self):
        self.fs = open("vsf", "r+")
        self.data = list(self.fs.read())
        self.fs.close()


    def __save(self):
        data = "".join(self.data)
        self.fs = open("vsf", "w+")
        self.fs.write(data)
        self.fs.close()


    def __lookup(self):
        pass


    def __find(self, path):
        pass


    def checkMap(self):
        line = ""
        for x in range(0, self.BLOCK_SIZE):
            byte = self.data[x]
            if x % 5 == 0:
                print(line)
                line = ""
            if x == len(self.INODE_MAP) or x == self.BLOCK_SIZE:
                print("")
            for y in range(0, 8):
                line += str((ord(byte) >> (7 - y)) & 0x01)
            line += " "


    def __newInode(self, itype):
        for x in range(0, len(self.INODE_MAP)):
            byte = self.data[x]
            for y in range(0, 8):
                if ((ord(byte) >> (7 - y)) & 0x01) == 0:
                    print("Info: new inode " + str(x * 8 + y))
                    self.data[x] = chr(ord(byte) | (0x80 >> y))
                    self.__initInode(x * 8 + y, itype)
                    return x * 8 + y 
        return -1


    def __delInode(self, no):
        x = no / 8
        self.data[x] = chr(ord(self.data[x]) & (~(0x80 >> no % 8)) % 256)
        self.__initInode(no, chr(0x00))
        print("Info: delete inode " + str(no))


    def __initInode(self, no, itype):
        inode = []
        for x in range(0, self.BLOCK_SIZE):
            inode += [chr(0x00)]
        inode[0] = itype

        if itype == 'D':
            blockNum = self.__newBlock()
            inode[1] = chr(blockNum / 256)
            inode[2] = chr(blockNum % 256)
        self.__writeInode(no, inode)


    def __getInode(self, no):
        inode = []
        inode = self.data[self.BLOCK_SIZE * (1 + no) : self.BLOCK_SIZE * (2 + no)]
        return inode


    def __setInode(self, no, itype, length, blocks):
        start = self.BLOCK_SIZE * (1 + no)

        self.data[start + 0] = itype
        
        if(itype == 'F'):
            self.data[start + 1] = chr(length / 256)
            self.data[start + 2] = chr(length % 256)
            offset = 2
        else:
            offset = 0

        for x in range(0, len(blocks)):
            block = blocks[x]
            self.data[start + offset + x * 2 + 1] = chr(block / 256)
            self.data[start + offset + x * 2 + 2] = chr(block % 256)


    def __writeInode(self, no, data):
        self.data[self.BLOCK_SIZE * (1 + no):self.BLOCK_SIZE * (2 + no)] = list(data)


    def __newBlock(self):
        for x in range(len(self.INODE_MAP), len(self.INODE_MAP) + self.BLOCK_SIZE):
            byte = self.data[x]
            for y in range(0, 8):
                if ((ord(byte) >> (7 - y)) & 0x01) == 0:
                    print("Info: new block " + str(x * 8 + y + 1))
                    self.data[x] = chr(ord(byte) | (0x80 >> y))
                    self.__initBlock(x * 8 + y + 1)
                    return x * 8 + y + 1
        return -1


    def __delBlocks(self, nos):
        for no in nos:
            x = no / 8
            self.data[x] = chr(ord(self.data[x]) & (~(0x80 >> no % 8) % 256))
            self.__initBlock(no)
            print("Info: delete block " + str(no))


    def __initBlock(self, no):
        for x in range(0, self.BLOCK_SIZE):
            self.data[self.dataStart + no * self.BLOCK_SIZE + x] = chr(0x00)


    def __getBlocks(self, inode):
        blocks = inode[1:]
        listbn = []
        #print blocks
        if inode[0] == 'F':
            offset = 2
        else:
            offset = 0
        for x in range(0, (self.BLOCK_SIZE - 1) / 2):
            blockNo = (ord(blocks[x * 2 + offset]) << 7) + ord(blocks[x * 2 + 1 + offset])
            if blockNo == 0:
                return listbn
            else:
                listbn += [blockNo]
        return listbn


    def __readBlocks(self, nos):
        return_data = []
        print("Read inodes: " + str(nos))
        for no in nos:
            return_data += (self.data[no * self.BLOCK_SIZE :
                                no * self.BLOCK_SIZE + self.BLOCK_SIZE])
        #print str(len(return_data))
        return return_data


    def __writeBlocks(self, nos, datas):
        if len(datas) < self.BLOCK_SIZE * len(nos):
            for x in range(len(datas), self.BLOCK_SIZE * len(nos)):
                datas += chr(0x00)

        for x in range(0, len(nos)):
            no = nos[x]
            self.data[no * self.BLOCK_SIZE : 
                      no * self.BLOCK_SIZE + self.BLOCK_SIZE] = datas[x * self.BLOCK_SIZE : (x + 1) * self.BLOCK_SIZE]


    def __getList(self, inode):
        lists = self.__readBlocks(self.__getBlocks(inode))
        lists = "".join(lists).strip().split('\n')
        listDir = {}

        if inode[0] == 'D':
            for l in lists:
                if ord(l[0]) != 0x00:
                    name  = l.split(':')[0]
                    inode = int(l.split(':')[1])
                    listDir.update({name:inode})

        return listDir


    def __setList(self, inode, newList):
        lists = ""
        for key in newList.keys():
            lists += (str(key) + ":" + str(newList[key]) + "\n")
        lists = list(lists)
        self.__writeBlocks(self.__getBlocks(inode), lists)


    def open(self, path):
        if path[0] != '/':
            path = self.curDir + '/' + path

        inode    = self.__getInode(0)
        inodeNum = 0
        if path == '/':
            return inodeNum, inode

        nods = path.split('/')[1:]

        listDir  = self.__getList(inode)
        for nod in nods[:-1]:
            for key in listDir.keys():
                if str(nod) == str(key):
                    inode    = self.__getInode(listDir[key])
                    inodeNum = listDir[key]
                    listDir = self.__getList(inode)

        found = False
        nod = nods[-1]
        for key in listDir.keys():
            if str(nod) == str(key):
                inode    = self.__getInode(int(listDir[key]))
                inodeNum = int(listDir[key])
                found    = True

        if found == False: # create file
            print("Info: file " + nod + " does not exist, create")
            inodeNum = self.__newInode('F')
            listDir.update({nod:str(inodeNum)})
            self.__setList(inode, listDir)
            inode = self.__getInode(inodeNum)
        return inodeNum, inode


    def close(self):
        pass


    def read(self, inodeNum):
        inode = self.__getInode(inodeNum)
        if inode[0] != 'F':
            print("Error: can't read a directory")
            return []
        else:
            length = (ord(inode[1]) << 8) + ord(inode[2])
            print("File length: " + str(length))
            data   = self.__readBlocks(self.__getBlocks(inode))[:length]
            return list(data)


    def write(self, inodeNum, data):
        #print "write: " + str(inodeNum)
        inode = self.__getInode(inodeNum)
        #print inode[0]
        if inode[0] != 'F':
            print("Error: can't write a directory ")
            return -1
        else:
            data   = list(data)
            length = len(data)
            blocks = self.__getBlocks(inode)
            #print blocks
            while length > len(blocks) * self.BLOCK_SIZE:
                newBlock = self.__newBlock()
                if newBlock == -1:
                    print("Error: not enough space")
                    return -2
                blocks += [newBlock]
            self.__writeBlocks(blocks, data)
            self.__setInode(inodeNum, 'F', length, blocks)
            return 0


    def cp(self, src, dst):
        if src[0] != '/':
            src = self.curDir + '/' + src
        if dst[0] != '/':
            dst = self.curDir + '/' + dst

        inumSrc, nodeSrc = self.open(src)
        inumDst, nodeDst = self.open(dst)

        data = self.read(inumSrc)
        self.write(inumDst, data)

        self.close() # not defined


    def rm(self, name):
        listDir = self.__getList(self.curInode)

        for key in listDir.keys():
            if str(key) == name:
                inodeNum = listDir[key]
                inode    = self.__getInode(inodeNum)
                if inode[0] == 'D':
                    print("Error: can't remove a directory, use rmdir")
                    return -1

                self.__delBlocks(self.__getBlocks(inode))
                self.__delInode(inodeNum)

                del listDir[key]
                self.__setList(self.curInode, listDir)
                print("Info: " + name + " removed")
                return 0

        print("Error: no such file")
        return -1



    def cd(self, name):
        pnod    = self.curInode
        listDir = self.__getList(pnod)

        if name == "..":
            self.curDir = "/".join(self.curDir.split('/')[:-1])

            if len(self.curDir) == 0:
                self.curDir = '/'
            inodeNum, self.curInode = self.open(self.curDir)
            return 0

        #print pnod
        if name not in listDir.keys():
            print("Error: No such directory")
            return -1
        else:
            if self.curDir[-1] != '/':
                path = (self.curDir + "/" + name)
            else:
                path = self.curDir + name
            inode = self.__getInode(listDir[name])
            if inode[0] != 'D':
                print("Error: can't goto a file")
                return -1
            else:
                self.curDir   = path
                self.curInode = inode
                return 0
            #print self.curInode
        return -1


    def ls(self):
        flist = self.__getList(self.curInode)
        #print flist
        result = []
        for key in flist.keys():
            result += [str(key)]
        return result


    def mkdir(self, name):
        pnod    = self.curInode
        listDir = self.__getList(pnod)

        if name in listDir.keys():
            print("Error: file " + name + " exists, can't create")
        else:
            inodeNum = self.__newInode('D')
            listDir.update({name:inodeNum})
            self.__setList(pnod, listDir)

        
    def rmdir(self, name):
        listDir = self.__getList(self.curInode)

        for key in listDir.keys():
            if str(key) == name:
                inodeNum = listDir[key]
                inode    = self.__getInode(inodeNum)
                if inode[0] == 'F':
                    print("Error: can't remove a file, use rm")
                    return -1

                listDel = self.__getList(inode)
                oldDir  = self.curDir
                self.curDir = self.curDir + '/' + name
                self.cd(name)
                for dkey in listDel.keys():
                    self.rm(str(dkey))
                self.cd("..")

                self.curDir = oldDir
                self.__delBlocks(self.__getBlocks(inode))
                self.__delInode(inodeNum)

                del listDir[key]
                self.__setList(self.curInode, listDir)
                print("Info: directory " + name + " removed")
                return 0

        print("Error: no such file")
        return -1


def cmd():
    fs = FileSystem()
    inode    = fs.curInode
    inodeNum = 0
    while True:
        c = raw_input(fs.curDir + " >> ")
        params = c.strip().split()

        if len(params) == 1:
            if params[0] == 'read':
                print("".join(fs.read(inodeNum)))
                continue
            
            if params[0] == 'close':
                inodeNum = 0
                continue

            if params[0] == 'ls':
                ls = fs.ls()
                for f in ls:
                    print(f)
                continue

            if params[0] == 'check':
                fs.checkMap()
                continue

            if params[0] == 'quit':
                break
        
        if len(params) == 2:
            if params[0] == 'open':
                inodeNum, inode = fs.open(params[1])
                continue

            if params[0] == 'cd':
                fs.cd(params[1])
                continue

            if params[0] == 'mkdir':
                fs.mkdir(params[1])
                continue

            if params[0] == 'write':
                fs.write(inodeNum, params[1])
                continue

            if params[0] == 'rm':
                fs.rm(params[1])
                continue

            if params[0] == 'rmdir':
                fs.rmdir(params[1])
                continue

        if len(params) == 3:
            if params[0] == 'cp':
                fs.cp(params[1], params[2])
                continue


        print("Error: invalid command")



if __name__ == "__main__":
    cmd()