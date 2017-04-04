#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains methods for signal processing
#There methods are intended to be used in conjuction with the raw data 
#passed to the uhf_channel object. They are intended to be called and return
#the signal properties of a given set of scan data

import numpy as np




def getproperties(signaldata):
    #top level function for processing the data
    #data in received in the form:
        #[centrefreq, freq, power_db, noise_floor_db]


    def __getmaxpower():
        #calculate the largest power value in data
        max_power = -1000
        for datapoint in powerdata:
            if datapoint > max_power:
                 max_power = datapoint
        max_power_relative = max_power
        max_power = max_power + noise_floor
        return max_power, max_power_relative

    def __getmeanpower():
        #calculate the mean power value for the data
        point_count = 0
        running_sum = 0
        for datapoint in powerdata:
            running_sum += datapoint
            point_count += 1
        mean_power_relative = running_sum / point_count
        mean_power = mean_power_relative + noise_floor
        return mean_power, mean_power_relative

    def __getsd():
        #calculate the standard deviation of the power data
        stddev_power = np.std(powerdata)
        return stddev_power



    noise_floor = signaldata[0][3]
    powerdata = [x[2] for x in signaldata]
    max_power, max_power_relative = __getmaxpower()
    mean_power, mean_power_relative = __getmeanpower()
    stddev_power = __getsd()
    vpp = max_power_relative
    ratio_vpp_std = vpp / stddev_power

    SPproperties = [max_power, max_power_relative, mean_power,
                    mean_power_relative, stddev_power, ratio_vpp_std,
                    noise_floor]
    
    return SPproperties


