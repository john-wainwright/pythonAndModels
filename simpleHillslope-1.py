# -*- coding: utf-8 -*-
"""

@author: John Wainwright
linking several 1-D leaky bucket models together to simulate a small hillslope
"""
import matplotlib.pyplot as plt

from leakyBucket import leakyBucket

if __name__ == '__main__':
#simple test with constant rainfall rate
    rainfall = 20. #20 mm/h 
    finalInfiltRate = 10. #10 mm/h so should produce HOF
    soilMoist = 0.04
    satSoilMoist = 0.38 #0.38 m/m saturated content
    transmissivity = 10.
    slope = 5. #degress - converted in the init    
    #now have three instances of the class soil1 is upslope of soil2 which is 
    #   upslope of soil3
    soil1 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, slope)
    soil2 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, slope)
    soil3 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, slope)
    #run storm as 60 steps of one minute each
    stormLength = 60
    timestep = 1. / 60. #in hours
    timeOut = []
    rainOut = []
    soilMoistOut = []
    overlandFlowOut = []
    subsurfFlowOut = []
    for time in range (0, stormLength):
        #update this timestep - nothing upslope of soil1 so zero runon and 
        #  subsurf inflow
        soil1.UpdateSoilMoist (rainfall, 0., 0., timestep)
        #but use values from soil1 to update soil2
        soil2.UpdateSoilMoist (rainfall, soil1.overlandFlow, soil1.subsurfFlow,
                               timestep)
        #and use values from soil2 to update soil3
        soil3.UpdateSoilMoist (rainfall, soil2.overlandFlow, soil2.subsurfFlow,
                               timestep)
        #output values at the bottom of the slope
        timeOut.append (time * timestep) #convert to h
        rainOut.append (rainfall)
        soilMoistOut.append (soil3.soilMoist)
        overlandFlowOut.append (soil3.overlandFlow)
        subsurfFlowOut.append (soil3.subsurfFlow)
        #look at downslope patterns of soil moisture
        print (time, soil1.soilMoist, soil2.soilMoist, soil3.soilMoist)
    
    # plot results
    fig, ax = plt.subplots ()
    # create a line using rainfall data
    line1, = ax.plot (timeOut, rainOut, label = 'rainfall')
    # add line to same plot using soil moisture data
    line2, = ax.plot (timeOut, soilMoistOut, label = 'soil moisture')
    # add line to same plot using overland flow data
    line3, = ax.plot (timeOut, overlandFlowOut, label = 'overland flow')
    # add line to same plot using subsurface flow data
    line4, = ax.plot (timeOut, subsurfFlowOut, label = 'subsurface flow')
    # add labels and legend 
    plt.xlabel ('time  [h]')
    plt.ylabel ('rate [mm/h]')
    ax.legend ()
    plt.show ()