import os
from numpy.lib.function_base import percentile
import tlsh
import random
import matplotlib.pyplot as plt
import json
import numpy as np
"""
import gmpy2
from gmpy2 import mpz
"""

COL = 28
ROW = 400
BITS = 512
THRESHOLD = 0.4
vectorsFile = "vectors20028.npy"
vectorsFileNoMask = "vectors20028NoMask.txt"
dataFilePath = "result20028"
hashesFile = "hashes20028.txt"
hashesFileNoMask = "hashes20028NoMask.txt"
hashesFileRowColTranspose = "hashes20028rct.txt"
curr_dir = os.path.dirname(os.path.realpath(__file__))

baselineIrises = []
baselineAttributes = []
irisCodeDataset = []    # USED FOR HASHING (STRING FORMAT)
attributes = []
vectors = []


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def rotateLeft(list_1, columnLen):
    return np.roll(list_1, -columnLen)


def rotateRight(list_1, columnLen):
    return np.roll(list_1, columnLen)


def hamming_distance(hash1, hash2):
    return sum(h1 != h2 for h1, h2 in zip(hash1, hash2))


def SimHash(vector, len):
    result = ""
    for i in range(len):
        matrixMul = np.dot(vector, vectors[i])
        if(matrixMul >= 0):
            result = result + "1"
        else:
            result = result + "0"
    return result


def getRandomVectors():
    allData = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()   
            allData.append(template)

    randomVectors = []
    while True:
        print(len(randomVectors))
        randomness = 0
        vectorr = np.random.choice([-1, 0, 1], size=COL*ROW)
        for x in allData:
            if(np.dot(x, vectorr) >= 0):
                randomness = randomness + 1

        percentage_randomness = randomness/len(allData)
        if(percentage_randomness >= 0.4 and percentage_randomness <= 0.6):
            randomVectors.append(vectorr)
            if(len(randomVectors) == BITS):
                break

    #with open(vectorsFile, 'w') as filehandle:
    np_randomVectors = np.array(randomVectors)
    np.save(vectorsFile, np_randomVectors, allow_pickle=True)
        #json.dump({'vectors': randomVectors}, filehandle, cls=NumpyEncoder)


def hashAllScans():
    hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            template = (
                (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
            hashes.append({"eye": attribute[-6:], "hash": SimHash(template, BITS)})
    with open(hashesFile, 'w') as filehandle:
        json.dump({'hashes': hashes}, filehandle, cls=NumpyEncoder)


def compareIrisHashes(target, same_eye):
    data = {}
    with open(hashesFile, 'r') as filehandle:
        data = json.load(filehandle)
    hashes = data["hashes"]
    for d in hashes:
        hash = d["hash"]
        subject = d["eye"]
        if target in subject:
            baselineIrises = getHashOfIrisScan(target)
            baselineAttributes.append(subject)
        else:
            irisCodeDataset.append(hash)
            attributes.append(subject)

    crosshashing = []
    total_accepted = 0
    same_eye_accepted = 0
    total_same_eye = 0
    best_match_str = ""
    best_match = BITS
    for y1, a1 in zip(irisCodeDataset, attributes):
        best = BITS
        best_dist = 0
        for y2 in baselineIrises:
            diff = hamming_distance(y1, y2)
            if(diff < best):
                best = diff
                best_dist = diff
            if(diff < best_match):
                best_match = diff
                best_match_str = a1

        same = best_dist <= THRESHOLD*BITS
        if(same_eye in a1):
            if(same):
                same_eye_accepted = same_eye_accepted + 1
            total_same_eye = total_same_eye + 1
        else:
            if(same):
                total_accepted = total_accepted + 1
        crosshashing.append(best_dist)
    """
    for x, y in zip(crosshashing, attributes):
        print(y + " : " + str(x))
    """
    FRR = (total_same_eye-same_eye_accepted) / total_same_eye
    FAR = total_accepted / int(len(irisCodeDataset))
    """
    print("FRR: " + str(FRR))
    print("FAR: " + str(FAR))
    print("Best match: " + best_match_str[-6:] + " : " + str(best_match))
    """
    return(FAR, FRR)


def compareHashes(target1, target2):
    hash1 = ""
    hash2 = ""
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target1 in attribute:
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                hash1 = SimHash(template, BITS)
            elif target2 in attribute:
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                hash2 = SimHash(template, BITS)
    print(hamming_distance(hash1, hash2))


def getHashOfIrisScan(target):
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target in attribute:
                local_hashes = []
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                local_hashes.append(SimHash(template, BITS))
                for i in range(1, 5):
                    local_hashes.append(
                        SimHash(rotateRight(template, COL*i*2), BITS))
                    local_hashes.append(
                        SimHash(rotateLeft(template, COL*i*2), BITS))
                return local_hashes

def printHashOfIrisScan(target):
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target in attribute:
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                print(hex(int(SimHash(template, BITS), 2)))
                

#getRandomVectors()

vectors = np.load(vectorsFile)

#hashAllScans()
# getHashOfIrisScan("S1008R01")
compareIrisHashes("229L02", "229L")
#printHashOfIrisScan("229L05")
#compareHashes("30R03", "30R05")
#print(getHashOfIrisScan("01R01"))
"""
total_scans = 0
total_FRR = 0
total_FAR = 0
data = {}
with open(hashesFile, 'r') as filehandle:
    data = json.load(filehandle)
    hashes = data["hashes"]
    for d in hashes:
        total_scans = total_scans + 1
        result = compareIrisHashes(d["eye"], d["eye"][:4])
        total_FAR = total_FAR + result[0]
        total_FRR = total_FRR + result[1]
print(str(total_FAR/total_scans), " : ", str(total_FRR/total_scans))
"""
