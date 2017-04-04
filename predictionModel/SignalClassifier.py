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
from sbs import SBS



def __traintest(X_train, X_test, y_train, y_test):

    #instance KNN model
    knn = KNeighborsClassifier(n_neighbors=5, p=2, metric='minkowski',
                               leaf_size = 30, weights = 'uniform')
    knn.fit(X_train, y_train)
    print knn.score(X_train, y_train)
    print knn.score(X_test, y_test)

    return knn

def sbs_run(model, X_data, y_targets):
    #code adapted from Python Machine Learning - Raschka
    sbs = SBS(model, k_features=1)
    sbs.fit(X_data, y_targets)
    k_feat = [len(k) for k in sbs.subsets_]
    plt.plot(k_feat, sbs.scores_, marker = 'o')
    plt.ylim([0.7, 1.1])
    plt.ylabel('Accuracy')
    plt.xlabel('Number of signal properties used')
    plt.grid()
    plt.show()
    for subset in sbs.subsets_:
        print subset

def __loadsorttest(datastore = 'training_data/cleaned_data', test = False):

    #load in sorted SP data
    X_data, y_targets = loadtraindata(datastore, 'D', 'D')
    X_train, X_test, y_train, y_test = train_test_split(
        X_data, y_targets, test_size = 0.3, random_state = 0)
    sc = StandardScaler()
    X_train_std = sc.fit_transform(X_train)
    X_test_std = sc.transform(X_test)
    model = __traintest(X_train_std, X_test_std, y_train, y_test)
    if test:
        knn = KNeighborsClassifier(n_neighbors=5, p=2, metric='minkowski',
                                   leaf_size = 30, weights = 'uniform')
        sbs_run(knn, X_train_std, y_train)
        plot3d(X_data[:,[0,1,4]], y_targets)
    
    return model

def loadmodel(datastore):

    model = __loadsorttest(datastore)
    
    return model

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
    ax.view_init(elev=25., azim=-145)
    ax.set_xlabel('Max power (dBm)')
    ax.set_ylabel('Relative max power (dBm)')
    ax.set_zlabel('Std dev power (dBm)')
    
    plt.show()
    






if __name__ == '__main__':
    __loadsorttest(test=True)

