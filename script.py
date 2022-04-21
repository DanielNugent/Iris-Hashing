from email.mime import base
import math
import os
from cv2 import sqrt
from numpy.lib.function_base import percentile
import random
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.ticker import PercentFormatter
import time
from random import randrange

COL = 28
ROW = 400
#file resolution codename
RES = "20028"
BITS = 512
THRESHOLD = 0.4
MAX_FA = 1000000*205*3*36500

vectorsFile = f"vectors{RES}.npy"
dataFilePath = f"result{RES}"
hashesFile = f"hashes{RES}.npy"
hashesPairFile = f"hashespair{RES}.npy"
hashesToBeStored = f"hashesbc{RES}.npy"
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

def padAndSplit512Hex(str):
    res = str[2:]
    while(len(res) != BITS/4):
        res = "0" + res
    return res

def globalMask():
    globalMask = np.zeros(ROW*COL)
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/Masks"):
        f = open(curr_dir+f"/{dataFilePath}/Masks/" + subject)
        data = json.load(f)
        for attribute in data:
            local_mask = np.array(data[attribute])
            globalMask = np.add(globalMask, local_mask)    
    globalMask = np.divide(globalMask, (ROW*COL))   
    globalMask[globalMask >= 0.06] = False
    globalMask[globalMask < 0.06] = True
    return globalMask

def rotateLeft(list, columnLen):
    return np.roll(list, -columnLen)


def rotateRight(list, columnLen):
    return np.roll(list, columnLen)


def hamming_distance(hash1, hash2):
    return np.count_nonzero(hash1!=hash2)/BITS


def decidability_index(mean_1, mean_2, std_1, std_2):
    return (abs(mean_1 - mean_2) / sqrt((std_1**2 + std_2**2) / 2)[0])[0]

def SimHash(vector, len, left=True):
    result = []
    midpoint = int(BITS/2)-1
    if(left):
        midpoint = 0

    for i in range(len):
        matrixMul = np.dot(vector, vectors[i+midpoint])
        if(matrixMul >= 0):
            result.append(1)
        else:
            result.append(0)
    return np.array(result)

def SimHashString(vector, len, left=True):
    result = ""
    midpoint = int(BITS/2)-1
    if(left):
        midpoint = 0

    for i in range(len):
        matrixMul = np.dot(vector, vectors[i+midpoint])
        if(matrixMul >= 0):
            result += "1"
        else:
            result += "0"
    return padAndSplit512Hex(hex(int(result, 2)))

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
        print("Getting the ", len(randomVectors), " vector")
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

    np_randomVectors = np.array(randomVectors)
    np.save(vectorsFile, np_randomVectors, allow_pickle=True)


def hashAllScans(rotations):
    print("Hashing the scans...")
    hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            local_hashes = []
            template = np.array(data[attribute])
            #template = np.logical_and(template, gm)*1
            local_hashes.append(SimHash(template, BITS))
            for i in range(1, rotations+1):
                templater_rotated = rotateRight(template, COL*i*2)
                templatel_rotated = rotateLeft(template, COL*i*2)
                local_hashes.append(
                    SimHash(templater_rotated, BITS))
                local_hashes.append(
                    SimHash(templatel_rotated, BITS))
            hashes.append({"eye": attribute[-6:], "hashes": local_hashes})
    np.save(hashesFile, hashes, allow_pickle=True)

def hashAllPairScans(rotations=0):
    hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        #separate the pairs
        left = []
        right = []
        person = ""
        index = 0
        for attribute in data:
            person = attribute[-6:-3]
            target_eye = attribute[-3] #L or R
            if(target_eye == "L"):
                left.append(data[attribute])
            else:
                right.append(data[attribute])

        print(person)
        for le in range(0, len(left)):
            for re in range(0, len(right)):
                local_hashes = []
                index += 1
                template_l = np.array(left[le])
                template_r = np.array(right[re])
                #local_hashes.append(np.concatenate([SimHash(template_l, int(BITS/2)), SimHash(template_r, int(BITS/2), False)]))           
                for i in range(-rotations, rotations+1):
                    for j in range(-rotations, rotations+1):
                        templatel_rotated = rotateRight(template_l, COL*i*2)
                        templater_rotated = rotateRight(template_r, COL*j*2)
                        local_hashes.append(np.concatenate([SimHash(templatel_rotated, int(BITS/2)), SimHash(templater_rotated, int(BITS/2), False)]))    
                
                l_id = f"00{le}"
                r_id = f"00{re}"
                if le>9:
                    l_id =  f"0{le}"
                if re>9:
                    r_id = f"0{re}"
                    
                hashes.append({"person": f"{person}-L{l_id}-R{r_id}", "hashes": local_hashes}) 

    np.save(hashesPairFile, hashes, allow_pickle=True)

def compareIrisHashes(target, same_eye, rotations=0):
    baselineIrises = []
    for d in hashes:
        hash = d["hashes"]
        #print(len(hash))
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
                template = data[attribute]
                hash1 = SimHash(template, BITS)
            elif target2 in attribute:
                template = data[attribute]
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
                template = np.array(data[attribute])
                splitHash = SimHashString(template, BITS)
                print(splitHash)
                return splitHash;
                
def compareAllIrisHashes(skip=1, rotations=0):
    start = time.process_time()
    total_scans = 0
    same_eye_accepted = 0
    total_same_eye = 0
    total_accepted = 0
    different_eye_comparisons = 0
    mean_1 = []
    mean_2 = []
    #print(len(hashes))
    total_comparisons = 0
    
    for i in range(0, len(hashes), skip):
        total_scans = total_scans + 1
        target_hashes = hashes[i]["hashes"][0: ((1+(rotations*2)))]
        target_eye = hashes[i]["eye"][:4]
        target_subject = hashes[i]["eye"]

        #print("working on : ", target_subject)
        for comparison_hash in hashes[i:]:
            # get the non-rotated hash
            chh = comparison_hash["hashes"][0]
            che = comparison_hash["eye"]
            #don't compare the same eye scan to itself
            if(target_subject in che):
                continue
            best_hd = 1
            for t_h_i in target_hashes:          
                hd = hamming_distance(t_h_i, chh)
                if(hd < best_hd):
                    best_hd = hd
            same = best_hd <= THRESHOLD
            total_comparisons = total_comparisons + 1
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
    plt.hist(mean_1, label="Same class", weights=np.ones(len(mean_1)) / len(mean_1), bins=50, fc=(0, 0, 1, 0.5))
    plt.hist(mean_2, label="Different class", weights=np.ones(len(mean_2)) / len(mean_2), bins=50, fc=(1, 0, 0, 0.5))
    plt.axvline(x=THRESHOLD, ymin=0.01, ymax=0.99, color='r', label="Threshold", linewidth=3)
    #plt.yscale("log")
    plt.title("Eye to Eye Comparison")
    plt.legend()
    plt.xlabel("Hamming distance")
    plt.ylabel("Frequency")
    std_1 = np.std(mean_1)
    std_2 = np.std(mean_2)
    mean_1 = np.mean(mean_1)
    mean_2 = np.mean(mean_2)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    #plt.spines['left'].set_color('white')        # setting up Y-axis tick color to red
    #plt.spines['top'].set_color('white')         #setting up above X-axis tick color to red
    print("Decidability index: ", decidability_index(mean_1, mean_2, std_1, std_2))
    print("Total Comparisons : ", total_comparisons)
    print("time taken : ", time.process_time() - start)
    plt.show()

def compareAllIrisHashesPerson(skip=1, rotations=0):
    start = time.process_time()
    total_scans = 0
    same_eye_accepted = 0
    total_same_eye = 0
    total_accepted = 0
    different_eye_comparisons = 0
    mean_1 = []
    mean_2 = []
    #print(len(hashes))
    total_comparisons = 0
    k = (1+(rotations*2))**2
    rr = (1+(rotations*2))**2
    print(len(hashes))
    
    for i in range(0, len(hashes), skip):
        total_scans = total_scans + 1
        target_hashes = hashes[i]["hashes"][0: k]
        target_person = hashes[i]["person"][0:3]
        target_id = hashes[i]["person"]
        target_left_eye = target_id[4:8]
        target_right_eye = target_id[9:]

        #print("working on : ", target_subject)
        for comparison_hash in hashes[i:]:
            # get the non-rotated hash
            chh = comparison_hash["hashes"][math.floor(rr/2)]
            chp = comparison_hash["person"]
            chpp = comparison_hash["person"][0:3]
            #left eye id
            chpl = comparison_hash["person"][4:8]
            #right eye id
            chpr = comparison_hash["person"][9:]
            #don't compare the same eye scan to itself
            if(target_id == chp or (chpp == target_person and (target_left_eye == chpl or target_right_eye == chpr))):
                continue
            best_hd = 1
            for t_h_i in target_hashes:          
                hd = hamming_distance(t_h_i, chh)
                if(hd < best_hd):
                    best_hd = hd
            same = best_hd <= THRESHOLD
            total_comparisons += 1
            # we are comparing the same eyes
            if(target_person == chpp):
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
    plt.hist(mean_1, label="Same class", weights=np.ones(len(mean_1)) / len(mean_1), bins=50, fc=(0, 0, 1, 0.5))
    plt.hist(mean_2, label="Different class", weights=np.ones(len(mean_2)) / len(mean_2), bins=50, fc=(1, 0, 0, 0.5))
    plt.axvline(x=THRESHOLD, ymin=0.01, ymax=0.99, color='r', label="Threshold", linewidth=3)
    #plt.yscale("log")
    plt.title("Eyes Combined Comparison")
    plt.legend()
    plt.xlabel("Hamming distance")
    plt.ylabel("Frequency")
    std_1 = np.std(mean_1)
    std_2 = np.std(mean_2)
    mean_1 = np.mean(mean_1)
    mean_2 = np.mean(mean_2)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    print("Decidability index: ", decidability_index(mean_1, mean_2, std_1, std_2))
    print("Total Comparisons : ", total_comparisons)
    print("time taken : ", time.process_time() - start)
    plt.show()

def getScansToBC():
    hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        #separate the pairs
        left = False
        right = False
        for attribute in data:
            target_eye = attribute[-3]
            if(target_eye == "L" and not left):
                left = True
                sh = SimHashString(np.array(data[attribute]), BITS)
                hashes.append(sh[0])
                hashes.append(sh[1])
            elif(target_eye == "R" and not right):
                right = True
                sh = SimHashString(np.array(data[attribute]), BITS)
                hashes.append(sh[0])
                hashes.append(sh[1])
    np.save(hashesToBeStored, hashes, allow_pickle=True)

def BCSearchSimulation(rotations=0):
    hashes = []
    test_hashes = []
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/MaskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/MaskedTemplates/" + subject)
        data = json.load(f)
        #separate the pairs
        left = False
        right = False
        twofa_l = randrange(MAX_FA)
        twofa_r = randrange(MAX_FA)
        for attribute in data:
            temp_hash = []
            target_eye = attribute[-3]
            template = np.array(data[attribute])
            sh = SimHash(template, BITS)
            if(target_eye == "L" and left):
                for i in range(1, rotations+1):
                    templater_rotated = rotateRight(template, COL*i*2)
                    templatel_rotated = rotateLeft(template, COL*i*2)
                    temp_hash.append(SimHash(templater_rotated, BITS))
                    temp_hash.append(SimHash(templatel_rotated, BITS))
                test_hashes.append({"hash": temp_hash, "tfa": twofa_l})
            elif(target_eye == "L" and not left):
                left = True
                temp_hash.append(sh)
                hashes.append({"hash": temp_hash, "tfa": twofa_l})
            elif(target_eye == "R" and right):
                for i in range(1, rotations+1):
                    templater_rotated = rotateRight(template, COL*i*2)
                    templatel_rotated = rotateLeft(template, COL*i*2)
                    temp_hash.append(
                        SimHash(templater_rotated, BITS))
                    temp_hash.append(
                        SimHash(templatel_rotated, BITS))
                test_hashes.append({"hash": temp_hash, "tfa": twofa_r})
            elif(target_eye == "R" and not right):
                right = True
                temp_hash.append(sh)
                hashes.append({"hash": temp_hash, "tfa": twofa_r})
    
    hashes = np.array(hashes)
    test_hashes = np.array(test_hashes)
    print(len(hashes), len(test_hashes))
    start = time.process_time()
    correct_match = 0
    for data in test_hashes:
        for bc_hash in hashes:
            best_dist = 1
            for rotation in data["hash"]:
                dist = hamming_distance(rotation, bc_hash["hash"])
                if(dist < best_dist):
                    best_dist = dist
            if(best_dist <= THRESHOLD):
                if(bc_hash["tfa"] == data["tfa"]):
                    correct_match += 1
    print(correct_match / len(test_hashes))
    print("time taken : ", time.process_time() - start)
    #np.save(hashesToBeStored, hashes, allow_pickle=True)

#the following line can be commented out after first run
getRandomVectors()
vectors = np.load(vectorsFile) #load the stored vectors
#the following line can be commented out after first run
hashAllScans(4)
#Uncomment the next line to hash the iris scans with the Left and Right eye combined
#hashAllPairScans(1)
hashes = np.load(hashesFile, allow_pickle=True) #load the stored hashes
#Uncomment the next line to load the iris scans with the Left and Right eye combined
#hashes = np.load(hashesPairFile, allow_pickle=True)
compareAllIrisHashes(skip=1, rotations=4)
#Uncomment the next line to compare the iris scans with the Left and Right eye combined
#compareAllIrisHashesPerson(skip=10, rotations=1)


"""
Setup
1. Download the iris template extractor https://github.com/bradishp/IrisTemplateExtractor
2. Find a dataset such as the CASIA-iris-interval and run the extraction code on the dataset
3. Store the results in the same path as this script
4. Call the results folder "result{angular_res}{radial_res}"
5. Change the "RES" constant to {angular_res}{radial_res} such as "20028" for 200 angular resolution and 28 radial resolution.
6. Change any constants to the necessary values - ROW = 2*angular_res and COL = radial_res
7. Run the program to hash and compare all scans in the dataset.
"""
