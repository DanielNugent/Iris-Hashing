# Iris Hashing

The extractor code is taken from Libor Masek's Iris extractor and Philip Braddish's codebase. The hashing script is my own work.

# Install the python deps

# Run

`py script.py`

You can change the eye scan you want to compare to all other scans in the script by passing `compareIrisHashes("S1{PersonNo}{L|R}{ScanNo}", "{PersonNo}_{L|R}")`

examples could be `compareIrisHashes("S1029L01", "029_L")`, `compareIrisHashes("S1001L01", "001_L")` etc

Go look in the `Database` folder and get examples, the first subdirectory are the `PersonNo`'s i.e. 001, 002 etc
Then are the Left and Right eye scans then the scans of that specific eye for specific person. You can input that file name in ```compareIrisHashes``` and 
```getHashOfIrisScan``` function as show. 

There are a few text folders for vector examples for different settings for the iris extractor, you don't need to change these, for the purpose of this example just call ```getHashOfIrisScan``` (which is a version of the SimHash LSH hash function) for any image you see in the database as I've already set up the parameters for this Dataset. You can try get the hash of a specific eye, register it on the WebApp then get another hash of a different scan of the same eye and see if the best match is that scan. 

i.e. call ```getHashOfIrisScan("S1001L01")```, register the hash, the call ```getHashOfIrisScan("S1001L03")``` and see if it finds the first hash as the closest match as these are scans of the same eye. 

If you want to extract the templates from the files, you need to use MatLab and install the the necessary tools/packages. Call ```exportdata.m``` with the appropriate parameters. For the purpose of this demonstration, I've already extracted the templates into the ```result20028``` folder. ```20028``` is just the angularRes (200) and radialRes (28) I used. These may have to be adjusted for different data sets.

