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
BITS = 256
THRESHOLD = 0.4
vectorsFile = "vectors20028.txt"
dataFilePath = "result20028"
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


def S3Hash(vector, len):
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
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            allData.append(data[attribute])

    randomVectors = []
    while True:
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

    with open(vectorsFile, 'w') as filehandle:
        json.dump({'vectors': randomVectors}, filehandle, cls=NumpyEncoder)


def compareIrisHashes(target, same_eye):

    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)
        for attribute in data:
            template = ((np.reshape(np.array(data[attribute]), (COL, ROW))).transpose()).flatten()
            if target in attribute:
                baselineIrises.append(S3Hash(template, BITS))
                """
                for i in range(1,5):
                    baselineIrises.append(S3Hash(rotateRight(template, COL*i), BITS))
                    baselineIrises.append(S3Hash(rotateLeft(template, COL*i), BITS))
                """
                baselineAttributes.append(attribute)    

            else:
                irisCodeDataset.append(S3Hash(template, BITS))
                attributes.append(attribute)

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
    print("FRR: " + str((total_same_eye-same_eye_accepted) / total_same_eye))
    print("FAR: " + str(total_accepted / int(len(irisCodeDataset))))
    print("Best match: " + best_match_str + " : " + str(best_match))

def getHashOfIrisScan(target):
    for subject in os.listdir(curr_dir+f"/{dataFilePath}/maskedTemplates"):
        f = open(curr_dir+f"/{dataFilePath}/maskedTemplates/" + subject)
        data = json.load(f)

        for attribute in data:
            if target in attribute:
                hash = hex(int(S3Hash(data[attribute], BITS)))
                print(hash)
                return hash


with open(vectorsFile, 'r') as filehandle:
    data = json.load(filehandle)
    vectors = data["vectors"]

getHashOfIrisScan("S1029L01")

compareIrisHashes("S1029L01", "029_L")