# Iris Hashing

# Install the python deps

# Run

`py script.py`

You can change the eye scan you want to compare to all other scans in the script by passing `compareIrisHashes("S1{PersonNo}{L|R}{ScanNo}", "{PersonNo}_{L|R}")`

examples could be `compareIrisHashes("S1029L01", "029_L")`, `compareIrisHashes("S1001L01", "001_L")` etc

Go look in the `Database` folder and get examples, the first subdirectory are the `PersonNo`'s i.e. 001, 002 etc
Then are the Left and Right eye scans then the scans of that specific eye for specific person. You can input that file name in ```compareIrisHashes``` and 
```getHashOfIrisScan``` function as show. 

There are a few text folders for vector examples for different settings for the iris extractor, you don't need to change these, for the purpose of this example just call ```getHashOfIrisScan``` for any image you see in the database as I've already set up the parameters for this Dataset. You can try get the hash of a specific eye, register it on the WebApp then get another hash of a different scan of the same eye and see if the best match is that scan.

i.e. call ```getHashOfIrisScan("S1029L01")```, register the hash, the call ```getHashOfIrisScan("S1029L03")``` and see if it finds the first hash as the closest match as these are scans of the same eye.

