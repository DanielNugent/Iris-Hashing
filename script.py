from email.mime import base
import os
from xmlrpc.client import boolean
from cv2 import sqrt
from numpy.lib.function_base import percentile
import random
import matplotlib.pyplot as plt
import json
import numpy as np
import matplotlib.pyplot as plt
"""
import gmpy2
from gmpy2 import mpz
"""

COL = 28
ROW = 400
BITS = 512
THRESHOLD = 0.40
vectorsFile = "vectors20028.npy"
vectorsFileNoMask = "vectors20028NoMask.txt"
dataFilePath = "result20028"
hashesFile = "hashes20028.npy"
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


def rotateLeft(list, columnLen):
    return np.roll(list, -columnLen)


def rotateRight(list, columnLen):
    return np.roll(list, columnLen)


def hamming_distance(hash1, hash2):
    return np.count_nonzero(hash1!=hash2)/BITS


def decidability_index(mean_1, mean_2, std_1, std_2):
    return (abs(mean_1 - mean_2) / sqrt((std_1**2 + std_2**2) / 2)[0])[0]

def SimHash(vector, len):
    result = []
    for i in range(len):
        matrixMul = np.dot(vector, vectors[i])
        if(matrixMul >= 0):
            result.append(1)
        else:
            result.append(0)
    return np.array(result)


def getRandomVectors():
    allData = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates")[0:200]:
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            template = np.array(data[attribute])
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


def hashAllScans(rotations):
    hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            local_hashes = []
            print("processing ", attribute)
            template = np.array(data[attribute])
            col_cat_templates = (
                (np.reshape(np.array(data[attribute]), (ROW, COL))).transpose()).flatten()
            local_hashes.append(SimHash(template, BITS))
            for i in range(1, rotations+1):
                templater_rotated = rotateRight(col_cat_templates, COL*i*2)
                templater_rotated = np.reshape(templater_rotated, (COL, ROW)).transpose().flatten()
                templatel_rotated = rotateLeft(col_cat_templates, COL*i*2)
                templatel_rotated = np.reshape(templatel_rotated, (COL, ROW)).transpose().flatten()
                local_hashes.append(
                    SimHash(templater_rotated, BITS))
                local_hashes.append(
                    SimHash(templatel_rotated, BITS))
            hashes.append({"eye": attribute[-6:], "hashes": local_hashes})
    np.save(hashesFile, hashes, allow_pickle=True)


def compareIrisHashes(target, same_eye, rotations=0):
    baselineIrises = []
    for d in hashes:
        hash = d["hashes"]
        print(len(hash))
        subject = d["eye"]
        if target in subject:
            baselineIrises = hash
            baselineAttributes.append(subject)
        else:
            irisCodeDataset.append(hash[0])
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
        same = best_dist <= THRESHOLD
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
    
    print("FRR: " + str(FRR))
    print("FAR: " + str(FAR))
    print("Best match: " + best_match_str[-6:] + " : " + str(best_match))
    
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


def getHashOfIrisScan(target, rotations=0):
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target in attribute:
                local_hashes = []
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                local_hashes.append(SimHash(template, BITS))
                
                for i in range(1, rotations+1):
                    local_hashes.append(
                        SimHash(rotateRight(template, COL*i*2), BITS))
                    local_hashes.append(
                        SimHash(rotateLeft(template, COL*i*2), BITS))
                
                return np.array(local_hashes)

def printHashOfIrisScan(target):
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target in attribute:
                template = (
                    (np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
                print(hex(int(SimHash(template, BITS), 2)))
                
def compareAllIrisHashes(skip=1, rotations=0):
    total_scans = 0
    same_eye_accepted = 0
    total_same_eye = 0
    total_accepted = 0
    different_eye_comparisons = 0
    mean_1 = []
    mean_2 = []
    print(len(hashes))
    
    for i in range(0, len(hashes), skip):
        total_scans = total_scans + 1
        target_hashes = hashes[i]["hashes"][0: (1+(rotations*2))]
        target_eye = hashes[i]["eye"][:4]
        target_subject = hashes[i]["eye"]

        #print("working on : ", target_subject)
        for comparison_hash in hashes:
            # get the non-rotated hash
            chh = comparison_hash["hashes"][0]
            che = comparison_hash["eye"]
            if(target_subject in che):
                continue
            best_hd = 1
            for t_h_i in target_hashes:          
                hd = hamming_distance(t_h_i, chh)
                if(hd < best_hd):
                    best_hd = hd
            same = best_hd <= THRESHOLD
            # we are comparing the same eyes
            if(target_eye in che):
                mean_1.append(best_hd)
                if(same):
                    same_eye_accepted = same_eye_accepted + 1
                total_same_eye = total_same_eye + 1
            # comparing different eyes
            else:
                mean_2.append(best_hd)
                if(same):
                    total_accepted = total_accepted + 1
                different_eye_comparisons = different_eye_comparisons + 1
    print("FRR: ", str((total_same_eye-same_eye_accepted) / total_same_eye), "\nFAR: ", str(total_accepted/different_eye_comparisons))   
    mean_1 = np.array(mean_1)
    mean_2 = np.array(mean_2)
    plt.hist(mean_1, label="Same class", weights=550*np.ones_like(mean_1), bins=50, fc=(0, 0, 1, 0.5))
    plt.hist(mean_2, label="Different class", bins=50, fc=(1, 0, 0, 0.5))
    plt.axvline(x=THRESHOLD, ymin=0.05, ymax=0.95, color='r', label="Threshold")
    #plt.yscale("log")
    plt.legend()
    plt.xlabel("Hamming distance")
    plt.ylabel("Frequency")
    plt.show()
    std_1 = np.std(mean_1)
    std_2 = np.std(mean_2)
    mean_1 = np.mean(mean_1)
    mean_2 = np.mean(mean_2)
    print("Decidability index: ", decidability_index(mean_1, mean_2, std_1, std_2))


getRandomVectors()
vectors = np.load(vectorsFile)
hashAllScans(4)
hashes = np.load(hashesFile, allow_pickle=True)
compareAllIrisHashes(skip=1, rotations=0)
# getHashOfIrisScan("S1008R01")
#compareIrisHashes("248R01", "248R")
#printHashOfIrisScan("229L05")
#compareHashes("30R03", "30R05")
#print(getHashOfIrisScan("01R01"))
#cProfile.run('compareAllIrisHashes(skip=10, rotations=0)')
"""
FRR:  0.3583895741214801 
FAR:  0.00011098588337977349
Decidability index:  2.695322230639374
FRR:  0.3177798464044682 
FAR:  0.0007480991405530656
Decidability index:  2.5081888341601406
2579
FRR:  0.3331393995811031 
FAR:  0.00021262241245309865
Decidability index:  2.682672047786663
"""