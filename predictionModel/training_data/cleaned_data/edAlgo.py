"""
Script to run energy detection algorithm on test data for comparison with kNN
model.
"""
from __future__ import division

from sklearn.model_selection import train_test_split
import os
import json



def loaddata():
    
    locationOne = []
    locationTwo = []
    locationThree = []
    locationFour = []
    locationFive = []
    locationSix = []

    
    for f in os.listdir(os.getcwd()):

        if not ".py" in f:
        
            with open(os.path.join(os.getcwd(), f)) as fd:
                d = json.load(fd)
                if "_0_" in f:
                  locationOne.append(d)
                  continue

                if "_1_" in f:
                  locationTwo.append(d)
                  continue

                if "_2_" in f:
                  locationThree.append(d)
                  continue

                if "_3_" in f:
                  locationFour.append(d)
                  continue

                if "_4_" in f:
                  locationFive.append(d)
                  continue

                if "_5_" in f:
                  locationSix.append(d)
                  continue

                print "Missed {}".format(f)


    locations = [locationOne, locationTwo, locationThree, locationFour,
              locationFive, locationSix]
    holder = []
    for location in locations:
        for scan in location:
            holder.append(scan)
    return holder

max_success = 0
max_primary = 0
max_secondary = 0
def runAlgo():
    #runs energy detection -114dBm algo on data

    holder = loaddata()
    x_values = []
    y_values = []
    for scan in holder:
        x_values.append(scan[1][0])
        y_values.append(scan[0])
    X_train, X_test, y_train, y_test = train_test_split(x_values, y_values,
                                                        test_size =0.3)
    global max_success

    def runTest(X, Y, primary_boundary, secondary_boundary):
        min_power = 0
        results = []
        expected = []

        for i in range(len(X)):
            maxpower = X[i]
            expected.append(Y[i])
            print "Expected : {}".format(Y[i])
            if maxpower < min_power:
                min_power = maxpower
            #Primary categorisation
            if maxpower > primary_boundary:
                results.append(2)
                print "Predicted : {}".format(2)
                continue
            #Secondary categorisation
            if maxpower > secondary_boundary:
                results.append(1)
                print "Predicted : {}".format(1)
                continue
            results.append(0)
            print "Predicted : {}".format(0)

        success_count = 0
        for i in range(len(expected)):
            if expected[i] == results[i]:
                success_count += 1
                print success_count
        success_rate = float(success_count) / float(len(expected))
        global max_success
        global max_primary
        global max_secondary
        if success_rate > max_success:
            max_success = success_rate
            max_primary = primary_boundary
            max_secondary = secondary_boundary

    runTest(X_train, y_train, -69, -95)
    print "Training set {}".format(max_success)
    print max_primary
    print max_secondary
    runTest(X_test, y_test, -69, -95)
    print "Testing set {}".format(max_success)
    





if __name__ == "__main__":
    runAlgo()
