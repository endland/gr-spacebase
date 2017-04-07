#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the training for the signal prediction model

import numpy as np
import os
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as Axes3D
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from DataCollect import loadtraindata



def __traintest(X_train, X_test, y_train, y_test):

    #instance KNN model
    knn = KNeighborsClassifier(n_neighbors=5, p=2, metric='minkowski',
                               leaf_size = 30, weights = 'uniform')
    knn.fit(X_train, y_train)
    print knn.score(X_train, y_train)
    print knn.score(X_test, y_test)

    return knn

def __loadsorttest(datastore = 'training_data/cleaned_data', test = False):

    #load in sorted SP data
    X_data, y_targets = loadtraindata(datastore)
    X_train, X_test, y_train, y_test = train_test_split(
        X_data, y_targets, test_size = 0.3, random_state = 0)
    sc = StandardScaler()
    sc.fit(X_train)
    X_train_std = sc.transform(X_train) 
    X_test_std = sc.transform(X_test)
    model = __traintest(X_train_std[:,[0,2,3,4,5,6]],
                        X_test_std[:,[0,2,3,4,5,6]], y_train, y_test)
    
    return model, sc

def loadmodel(datastore):

    model, sc = __loadsorttest(datastore)
    
    return model, sc

def plot3d(X_data, y_targets):

    #plot data in 3 planes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    i = 0
    PrimaryX = []
    PrimaryY = []
    PrimaryZ = []
    SecondaryX = [] 
    SecondaryY = []
    SecondaryZ = []
    UnoccupiedX = []
    UnoccupiedY = []
    UnoccupiedZ = []

    
    Secondary = []
    Unoccupied = []
    for point in y_targets:
        if point == 0:
            UnoccupiedX.append(X_data[i][0])
            UnoccupiedY.append(X_data[i][1])
            UnoccupiedZ.append(X_data[i][2])
            i+=1
        if point == 1:
            SecondaryX.append(X_data[i][0])
            SecondaryY.append(X_data[i][1])
            SecondaryZ.append(X_data[i][2])
            i+=1
        if point == 2:
            PrimaryX.append(X_data[i][0])
            PrimaryY.append(X_data[i][1])
            PrimaryZ.append(X_data[i][2])
            i+=1
        if point == 4:
            #Used for unknown, currently obsoltete
            i+=1
    ax.scatter(UnoccupiedX, UnoccupiedY, UnoccupiedZ, c='g', marker
               ='o', label = 'Unoccupied')
    ax.scatter(SecondaryX, SecondaryY, SecondaryZ, c='b', marker
               ='^', label = 'Secondary')
    ax.scatter(PrimaryX, PrimaryY, PrimaryZ, c='r', marker
               ='x', label = 'Primary')
    ax.legend(bbox_to_anchor=(1.10,1.10))
    ax.autoscale(tight = True)
    ax.view_init(elev=25., azim=-125)
    ax.set_xlabel('Max power (dBm)')
    ax.set_ylabel('Relative mean power (dBm)')
    ax.set_zlabel('Std dev power (dBm)')
    
    plt.show()
    






if __name__ == '__main__':
    __loadsorttest(test=True)

