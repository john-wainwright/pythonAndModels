# -*- coding: utf-8 -*-
"""

@author: John Wainwright
linking several 1-D leaky bucket models together to simulate a small hillslope
"""
import matplotlib.pyplot as plt

from leakyBucket import leakyBucket

if __name__ == '__main__':
#simple test with constant rainfall rate
    #just change stormRainfall to modify both implementations
    stormRainfall = 20. #20 mm/h
    rainfall = stormRainfall 
    finalInfiltRate = 5. #5 mm/h so should produce HOF
    soilMoist = 0.04 #assumes dry soil
    satSoilMoist = 0.38 #assumes 0.38 m/m saturated content
    transmissivity = 10.
    depth = 500.
    slope = 5. #degress - converted in the init    
    #but now have three instances of the class soil1 is upslope of soil2 
    #   which is upslope of soil3
    soil1 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope)
    soil2 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope)
    soil3 = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope)
    #run storm as 60 steps of one minute each
    stormLength = 60
    timestep = 1. / 60. #in hours
    timeOut = []
    rainOut = []
    soilMoistOut = []
    overlandFlowOut = []
    subsurfFlowOut = []
    for time in range (0, stormLength):
        #update this timestep - nothing upslope of soil1 so zero runon and subsurf inflow
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
    plt.draw ()        
    plt.pause (0.001)
    
    #alternative implementation as a list of cells
    catena = []
    #add cell at top of slope
    catena.append (leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope))
    #add next cell down
    catena.append (leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope))
    #add next cell down
    catena.append (leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope))
    #tell second cell to receive inflows from topmost cell
    catena [1].upslopeCells.append (0)
    #tell third cell to receive inflows from second cell
    catena [2].upslopeCells.append (1)
    #outputs
    timeOut1 = []
    rainOut1 = []
    soilMoistOut1 = []
    overlandFlowOut1 = []
    subsurfFlowOut1 = []
    rainfall = stormRainfall 
    #simulation loop
    for time in range (0, stormLength):
        #loop through each cell in the catena
        for thisSoil in catena:
        #accumulate runon and inflowing SSF from upslope cells
            runon = 0.
            subsurfInflow = 0.
            #find all upslope cells (a bit of overkill -- we've only set it up
            #   for one each)
            for upslope in thisSoil.upslopeCells:
                runon = runon + catena [upslope].overlandFlow
                subsurfInflow = subsurfInflow + catena [upslope].subsurfFlow
            #update current cell    
            thisSoil.UpdateSoilMoist (rainfall, runon, 
                                               subsurfInflow , timestep)
        #output values at the bottom of the slope
        timeOut1.append (time * timestep) #convert to h
        rainOut1.append (rainfall)
        soilMoistOut1.append (catena [2].soilMoist)
        overlandFlowOut1.append (catena [2].overlandFlow)
        subsurfFlowOut1.append (catena [2].subsurfFlow)

    #check the two implementations give the same results
    dSoilMoist = 0.
    dOF = 0.
    dSSF = 0.
    for i in range (0, len (soilMoistOut)):
        dSoilMoist = dSoilMoist + abs (soilMoistOut [i] - soilMoistOut1 [i])
        dOF = dOF+ abs (overlandFlowOut [i] - overlandFlowOut1 [i])
        dSSF = dSoilMoist + abs (subsurfFlowOut [i] - subsurfFlowOut1 [i])
    print ('Total differences in implementations:')
    print ('Soil moisture {0}, overland flow {1}, subsurface flow {2}'.format 
           (dSoilMoist, dOF, dSSF))
        
    # plot results
    fig1, ax1 = plt.subplots ()
    # create a line using rainfall data
    line11, = ax1.plot (timeOut1, rainOut1, label = 'rainfall')
    # add line to same plot using soil moisture data
    line12, = ax1.plot (timeOut1, soilMoistOut1, label = 'soil moisture')
    # add line to same plot using overland flow data
    line13, = ax1.plot (timeOut1, overlandFlowOut1, label = 'overland flow')
    # add line to same plot using subsurface flow data
    line14, = ax1.plot (timeOut1, subsurfFlowOut1, label = 'subsurface flow')
    # add labels and legend 
    plt.xlabel ('time  [h]')
    plt.ylabel ('rate [mm/h]')
    ax1.legend ()
    plt.show ()        

