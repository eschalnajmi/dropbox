import os
import socket
import sys
from threading import Thread

def getdir():
    '''
    Gets the destination directory path from the user.
    :return: destination directory path and list of files already in the directory
    '''
    addedfiles = []
    if len(sys.argv) < 2:
        destination = "destination"
    else:
        destination = sys.argv[1]

    if not(os.path.exists(destination)):
        os.mkdir(destination)
        print(f"Created directory {destination}\n\n")
    else:
        for f in os.listdir(destination):
            if not(os.path.isdir(os.path.join(destination, f))):
                addedfiles.append(f)
            
    return destination, addedfiles

def RunServer(destination, addedfiles, client, addr):
    '''
    Actual server code that receives files from the client.
    :param destination: destination directory path
    :param addedfiles: list of files already in the directory
    :param client: client socket
    :param addr: client address
    '''
    while True:
        filename = client.recv(4096).decode()
        if filename == "": break
        if filename[0:3] == "rm ":
            os.remove(os.path.join(destination, filename[3:]))
            print(f"deleted {filename[3:]}")
            client.send("Success".encode())
            continue

        if "/" in filename:
            tempdestination = destination
            dirs = filename.split("/")
            for d in dirs[:-1]:
                tempdestination = os.path.join(tempdestination, d)
                if not(os.path.exists(tempdestination)):
                    os.mkdir(tempdestination)
                    print(f"Created directory {tempdestination}\n\n")

        file = open(os.path.join(destination, filename),"w")
        client.send("Success".encode())

        iterations = int(client.recv(4096).decode())
        client.send("Success".encode())
    
        contents = ""
        for i in range(iterations):
            recvcontents = client.recv(4096).decode()
            if recvcontents != f"\0":
                contents += recvcontents
            else:
                contents = f"\0"
                break
        
        file.write(contents)
        file.flush()
        file.close()
        
        client.send("Success".encode())

        addedfiles.append(filename)
    client.close()

def connect(destination,addedfiles):
    '''
    Connects to the client and receives files from the client.
    :param destination: destination directory path
    :param addedfiles: list of files already in the directory
    '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0',8080))
    server.listen(5)

    while True:
        try:
            client, addr = server.accept()
            thread = Thread(target=RunServer, args=(destination, addedfiles, client, addr))
            thread.start()
        except Exception as e:
            print(f"Error: {e}")
            break
    
    client.close()
    thread.join()
        
if __name__ == "__main__":
    destination, addedfiles = getdir()
    connect(destination, addedfiles)