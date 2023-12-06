"""

@author: John Wainwright
Simple instance of a 1-D leaky bucket model for soil hydrology
Mostly based on Wainwright and Parsons (2002) WRR

Variables:
    input variables (parameters)
    rainfall            rainfall rate in mm/h 
    finalInfiltRate     final infilration rate in mm/h 
    satSoilMoist        saturated soil moisture content in m/m
    transmissivity      soil transmissivity (unsaturated flow)
    depth               soil depth in mm
    slope               surface slope in degrees   
    runonRate           rate of runon arriving from upslope in mm/h
    subsurfInflow       subsurface inflow from upslope  in mm/h

    variables describing the process
    soilMoist           current value of soil moisture content in m/m
    infiltRate          current rate of infiltration in mm/h
    overlandFlow        current rate of overland flow in mm/h
    subsurfFlow         current rate of subsurface flow in mm/h
    drainage            current rate of drainage from the base of the
                        soil profile in mm/h
    depth               depth of soil profile in mm
    theta               relative soil moisture (= soilMoist / satSoilMoist)
    inflowRate          rainfall + runon arriving at a point in mm/h

    variables used in the main program
    stormLength         length of storm event in minutes
    timestep            length of step during storm event in minutes
    timeOut             used to plot and output time of calculation
    rainOut             used to plot and output rainfall rate
    soilMoistOut        used to plot and output current soil moisture
    overlandFlowOut     used to plot and output overland flow rate
    subsurfFlowOut      used to plot and output subsurface flow rate
    time                index in main loop to run through each time step

"""

import matplotlib.pyplot as plt
from math import pi, sin, cos, exp

#simple test with constant rainfall rate
rainfall = 20. # mm/h 
finalInfiltRate = 12. # mm/h
initialSoilMoist = 0.04 #assumes dry soil
initialSatSoilMoist = 0.38 #assumes 0.38 m/m saturated content
transmissivity = 10.
depth = 500.
slope = 5.    

#parameters
finalInfiltPrime = finalInfiltRate - 1. 
satSoilMoist = initialSatSoilMoist * depth
slope = slope / (180. / pi) #convert to radians        
runonRate = 0.  # runon from upslope
subsurfInflow = 0.  #subsurface inflow from upslope

#state variables
soilMoist = initialSoilMoist * depth

#process variables
infiltRate = 0.
overlandFlow = 0.
subsurfFlow = 0.
drainage = 0.
depth = 0.
theta = 0. #relative soil moisture (= soilMoist / satSoilMoist)

#main part of program to run storm event
#run storm as 60 steps of one minute each
stormLength = 60
timestep = 1. / 60. #in min
timeOut = []
rainOut = []
soilMoistOut = []
overlandFlowOut = []
subsurfFlowOut = []

with open ("LeakyBucket0ResultsFile.txt", 'w') as outFile:   
    #output header
    outFile.write ("time rainfall infiltrationRate subsurfFlow " + 
                   "drainage soilMoist overlandFlow\n")

    for time in range (0, stormLength):
        #calculate current value of infiltration rate
        infiltrationRate = finalInfiltPrime + (satSoilMoist / soilMoist)
        #calculate Hortonian overland flow
        inflowRate = rainfall + runonRate
        if (inflowRate > infiltrationRate):
            overlandFlow = inflowRate - infiltrationRate
        else:
            overlandFlow = 0.
        #calculate subsurface flow and drainage
        ssfConst = finalInfiltRate * exp (-(satSoilMoist - soilMoist) / 
                                          transmissivity)
        subsurfFlow = ssfConst * sin (slope)
        if subsurfFlow < 0:
            print (satSoilMoist, soilMoist, ssfConst, slope, 
                   sin (slope), subsurfFlow)
        drainage = ssfConst * cos (slope)
        #update soil moisture
        dSoilMoist = timestep * (rainfall + runonRate + subsurfInflow - 
                                 overlandFlow - subsurfFlow - drainage)
        soilMoist = soilMoist + dSoilMoist
        #check if saturation overland flow has occurred and if so add it to HOF 
        #  and stop bucket overflow
        if (soilMoist > satSoilMoist):
            satOF = satSoilMoist - soilMoist
            overlandFlow = overlandFlow + satOF
            soilMoist = satSoilMoist
        #update relative soil moisture [mm/mm]
        theta = soilMoist / satSoilMoist

        print (time, rainfall, infiltrationRate, subsurfFlow, 
               drainage, soilMoist, overlandFlow)
        outFile.write (str (time) + " " + str (rainfall) + " " + 
                       str (infiltrationRate) + " " + str (subsurfFlow) + 
                       " " + str (drainage) + " " + str (soilMoist) + " " + 
                       str (overlandFlow) + "\n")
        timeOut.append (time * timestep) #convert to h
        rainOut.append (rainfall)
        soilMoistOut.append (soilMoist)
        overlandFlowOut.append (overlandFlow)
        subsurfFlowOut.append (subsurfFlow)
    #main time loop ends here because of indentation
#output file closes here because of indentation
    
# end of storm -- plot results
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

fig.savefig ("leakyBucketResults.jpg")  #save the figure for future use
        
                        