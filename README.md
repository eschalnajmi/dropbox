## DropBox

A  multi-threaded client-server network implemented in python to track a source directory and update the destination directory to contain all the same folders and files.

## How to run

1. Navigate to folder containing ```client.py``` and ```server.py```
2. Open a terminal and run the following command:
```
python server.py <destination-directory>
```
3. Open another terminal and run the following command:
```
python client.py <source-directory>
```

## Contains
- ```test``` - a folder containing all files I used for testing this network.
- ```client.py``` - a script for the client side of the network.
- ```server.py``` - a script for the server side of the network.

## Functionality
- Able to update the destination folder in live time for any changes to the source folder.
- Multiple clients are able to connect to the same server.
- Large text files which are >4096 bytes are chunked into smaller 4096 packets and passed to the server.
- If no destination directory is provided, the server creates a directory called destination.
- If the source directory does not exist, a directory with that name is created in the current working directory.

## Limitations
- Currently, if no source directory is provided the program will exit entirely.
- I was unable to optimise data transfer by avoiding uploading the same partial files (files sharing partially the same content) multiple times. The only method I could think of to do this is to store all chunks created in an array and parse each new chunk through that to see if they are identical and if so upload the previous chunk instead. However, I think this would negatively affect my code in terms of time and space complexity, and due to time constraints I was unable to implement it.