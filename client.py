import os
import socket
import hashlib
import sys
import math

def getdir():
    '''
    Gets the source directory path from the user, if no path entered it returns the current working directory.
    :return: source directory path
    '''

    if len(sys.argv) < 2:
        source = os.getcwd()
        os.chdir("../")
        return source.split("/")[-1], True
    
    if not(os.path.exists(sys.argv[1])):
        os.mkdir(sys.argv[1])

    return sys.argv[1], False

def sendfiles(removedfiles, newfiles, source, parentdir):
    '''
    Sends all new files to the server.
    :param newfiles: list of new files
    :param source: source directory path
    :return: list of successfully added files
    '''
    successfullyadded = []
    newcontents = [] # stores hash of new contents
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('0.0.0.0',8080))

    # check if going up a directory
    if parentdir:
        client.send("../".encode())
        print("asked to go to parent dir")
        server_msg = client.recv(4096).decode()
        parentdir = False
        if server_msg != "Success":
            print("Error with changing directory")
            return []

    # check for any removed files
    if len(removedfiles) > 0:
        for f in removedfiles:
            client.send(f"rm {f}".encode())
            server_msg = client.recv(4096).decode()
            if server_msg != "Success":
                print(f"Error with removing file {f}")
                return []

    # check for any new files
    if len(newfiles) == 0:
        return [],[]

    # send new files to server
    for f in newfiles:
        iterations = 1

        client.send(f"{f}".encode())

        server_msg = client.recv(4096).decode()
        if server_msg != "Success":
            print(f"Error with file {f}")
            return []
        
        contents = open(os.path.join(source, f),"r").read()

        if contents == "":
            contents = f"\0"

        if sys.getsizeof(contents) > 4096:
            iterations = math.ceil(sys.getsizeof(contents)/4096) # chunking files into 4096 byte packets

        client.send(f"{iterations}".encode())
        server_msg = client.recv(4096).decode()
        if server_msg != "Success":
            print(f"Error with file {f}")
            return []
        
        client.send(f"{contents}".encode())
        server_msg = client.recv(4096).decode()
        if server_msg != "Success":
            print(f"Error with file {f}")
            return []
        
        successfullyadded.append(f)
        newcontents.append(hashlib.md5(contents.encode()).hexdigest())

    client.close()
    return successfullyadded, newcontents

def all_directories(path):
    '''
    Returns all directories in the path.
    :param path: path to search for directories
    :return: list of directories
    '''
    allfiles = []
    curpath = path

    # skip files beginning with a . due to utf encoding error
    if path.split("/")[-1][0] == ".":
        return allfiles
    
    for d in os.listdir(path):
        if not(os.path.isdir(os.path.join(curpath, d))):
            allfiles.append(os.path.join(curpath, d))
        else:
            allfiles+=all_directories(os.path.join(curpath, d))
    return allfiles

def getfiles(source, parentdir):
    '''
    Gets all files from the source directory and sends any new ones to the server.
    :param source: source directory path
    '''
    addedfiles=[]
    addedcontents=[] # stores hash of added contents
    dirpaths = []

    for f in os.listdir(source):
        if not(os.path.isdir(os.path.join(source, f))) and f[0] != ".":
            try:
                addedcontents.append(hashlib.md5(open(os.path.join(source, f),"r").read().encode()).hexdigest())
            except:
                print(f'error with file {f}')
        else:
            dirs = all_directories(os.path.join(source,f))
            for d in dirs:
                addedcontents.append(hashlib.md5(open(d,"r").read().encode()).hexdigest())
                dirpaths.append(d[(len(source)+1):])
        

    count = 0
    while True:
        # get all files and directories within folder
        allfilenames = [f for f in os.listdir(source) if not(os.path.isdir(os.path.join(source, f)))]
        for f in os.listdir(source):
            if os.path.isdir(os.path.join(source, f)):
                dirs = all_directories(os.path.join(source,f))
                for d in dirs:
                    if d[(len(source)+1):] not in dirpaths:
                        dirpaths.append(d[(len(source)+1):])

        allfilenames+=dirpaths

        newfiles = [f for f in allfilenames if f not in addedfiles]

        removedfiles = [f for f in addedfiles if f not in allfilenames]

        # remove deleted files from addedfiles array
        for f in removedfiles:
            addedcontents.pop(addedfiles.index(f))
            addedfiles.remove(f)

        # check if any files have been modified
        for i, f in enumerate(addedfiles):
            if hashlib.md5(open(os.path.join(source, f),"r").read().encode()).hexdigest() != addedcontents[i]:
                newfiles.append(f)
                addedcontents.pop(i)
                addedfiles.pop(i)

        # check if there are new or deleted files
        if len(newfiles)==0 and len(removedfiles)==0:
            continue

        try:
            # send files to server
            newlyaddedfiles,newcontents=sendfiles(removedfiles, newfiles, source, parentdir)
            if parentdir:
                parentdir = False
            addedfiles+=newlyaddedfiles
            addedcontents+=newcontents
            count+=1
            
        except Exception as e:
            print(f"Error: {e}")
            return


if __name__ == "__main__":
    # get source directory path and send files to server
    source, parentdir = getdir()
    getfiles(source, parentdir)