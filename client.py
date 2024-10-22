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
        print("Please provide a source directory path.")
        exit(1)
    
    if not(os.path.exists(sys.argv[1])):
        os.mkdir(sys.argv[1])

    return sys.argv[1]

def sendfiles(newfiles, source):
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
            iterations = math.ceil(sys.getsizeof(contents)/4096)

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
    for d in os.listdir(path):
        if not(os.path.isdir(os.path.join(curpath, d))):
            allfiles.append(os.path.join(curpath, d))
        else:
            allfiles+=all_directories(os.path.join(curpath, d))
    return allfiles

def getfiles(source):
    '''
    Gets all files from the source directory and sends any new ones to the server.
    :param source: source directory path
    '''
    addedfiles=[]
    addedcontents=[] # stores hash of added contents
    dirpaths = []

    for f in os.listdir(source):
        if not(os.path.isdir(os.path.join(source, f))):
            addedcontents.append(hashlib.md5(open(os.path.join(source, f),"r").read().encode()).hexdigest())
        else:
            dirs = all_directories(os.path.join(source,f))
            for d in dirs:
                addedcontents.append(hashlib.md5(open(d,"r").read().encode()).hexdigest())
                dirpaths.append(d[(len(source)+1):])
        

    count = 0
    while True:
        allfilenames = [f for f in os.listdir(source) if not(os.path.isdir(os.path.join(source, f)))]
        for f in os.listdir(source):
            if os.path.isdir(os.path.join(source, f)):
                dirs = all_directories(os.path.join(source,f))
                for d in dirs:
                    if d[(len(source)+1):] not in dirpaths:
                        dirpaths.append(d[(len(source)+1):])

        allfilenames+=dirpaths

        newfiles = [f for f in allfilenames if f not in addedfiles]

        for i, f in enumerate(addedfiles):
            if hashlib.md5(open(os.path.join(source, f),"r").read().encode()).hexdigest() != addedcontents[i]:
                newfiles.append(f)
                addedcontents.pop(i)
                addedfiles.pop(i)

        if len(newfiles)==0:
            continue

        try:
            newlyaddedfiles,newcontents=sendfiles(newfiles, source)
            addedfiles+=newlyaddedfiles
            addedcontents+=newcontents
            count+=1
            
        except Exception as e:
            print(f"Error: {e}")
            return


if __name__ == "__main__":
    source = getdir()
    getfiles(source)