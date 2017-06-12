#gr-spacebase project github.com/wirrell/gr-spacebase
#data collection from training scan files for model training
#includes exclusion options to exclude certain named files from the trainin set
#if desired
import os
import json
import numpy as np

def loadtraindata(store, ex1 = False, ex2 = False):


    k = len(os.listdir(store))
    if ex1 and ex2:
        for f in os.listdir(store):
            if ex1 in f:
                k = k-1
                continue
            if ex2 in f:
                k = k-1
                continue
        
    SP_bank = np.empty([k, 7])
    SP_targets = np.empty([k])
    i = 0 
    for f in os.listdir(store):
        f = store + '/{}'.format(f)
        if ex1 and ex2:
            if ex1 in f:
                continue
            if ex2 in f:
                continue
        with open(f) as fp:
            print f
            d = json.load(fp)
            if d[0] ==4:
                print f
            SP_bank[i] = d[1]
            #if d[0] == 2:
            #    SP_targets[i] = 1
            #    i+=1
            #    continue
            SP_targets[i] = d[0]
            i += 1

    return SP_bank, SP_targets


if __name__ == "__main__":
    loadtraindata('training_data/cleaned_data', 'M', 'C')



