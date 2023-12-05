"""

@author: John Wainwright
Simple instance of a 1-D leaky bucket model for soil hydrology
Mostly based on Wainwright and Parsons (2002) WRR

Variables:
    Used to initialize the class
    initialSatInfilt        final infilration rate in mm/h
    initialSoilMoist        initial soil moisture value in m/m
    initialSatSoilMoist     initial saturated soil moisture value in m/m
    initialTransmissivity   initial transmissivity value 
    initialDepth            initial depth of soil in mm
    initialSlope            initial slope angle in degrees
    upslopeCells            list of cells upslope of this one
    
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

    variables used in the test program
    rainfall            rainfall rate in mm/h 
    finalInfiltRate     final infilration rate in mm/h 
    soilMoist           current value of soil moisture content in m/m
    satSoilMoist        saturated soil moisture content in m/m
    transmissivity      soil transmissivity (unsaturated flow)
    depth               soil depth in mm
    slope               surface slope in degrees   
    runonRate           rate of runon arriving from upslope in mm/h
    subsurfInflow       subsurface inflow from upslope  in mm/h
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


class leakyBucket:
    def __init__ (self, initialSatInfilt = 0., initialSoilMoist = 0., 
                  initialSatSoilMoist = 0., initialTransmissivity = 0., 
                  initialDepth = 0., initialSlope = 0.):
        #parameters
        self.satInfilt = initialSatInfilt
        self.satInfiltPrime = self.satInfilt - 1. 
        self.satSoilMoist = initialSatSoilMoist * initialDepth
        self.transmissivity = initialTransmissivity
        self.slope = initialSlope / (180. / pi) #convert to radians        
        #state variables
        self.soilMoist = initialSoilMoist * initialDepth
        #process variables
        self.infiltRate = 0.
        self.overlandFlow = 0.
        self.subsurfFlow = 0.
        self.drainage = 0.
        self.depth = 0.
        self.theta = 0. #relative soil moisture (= soilMoist / satSoilMoist)
        #list of upslope cells when used in landscape
        self.upslopeCells = []
        
    def SetParameters (self, initialSatInfilt, initialSoilMoist, 
                       initialSatSoilMoist, initialTransmissivity, 
                       initialDepth, initialSlope):
        #parameters
        self.satInfilt = initialSatInfilt
        self.satInfiltPrime = self.satInfilt - 1. 
        self.satSoilMoist = initialSatSoilMoist * initialDepth
        self.transmissivity = initialTransmissivity
        self.depth = initialDepth
        self.slope = initialSlope  #assume already in radians        
        #state variables
        self.soilMoist = initialSoilMoist * initialDepth
    
    def UpdateSoilMoist (self, rainfallRate, runonRate, subsurfInflow, timestep):
        #calculate current value of infiltration rate
        self.infiltRate = self.satInfiltPrime + (self.satSoilMoist / 
                                                 self.soilMoist)
        #calculate Hortonian overland flow
        inflowRate = rainfallRate + runonRate
        if (inflowRate > self.infiltRate):
            self.overlandFlow = inflowRate - self.infiltRate
        else:
            self.overlandFlow = 0.
        #calculate subsurface flow and drainage
        ssfConst = self.satInfilt * exp (-(self.satSoilMoist - self.soilMoist) / 
                                         self.transmissivity)
        self.subsurfFlow = ssfConst * sin (self.slope)
        if self.subsurfFlow < 0:
            print (self.satSoilMoist, self.soilMoist, ssfConst, self.slope, 
                   sin (self.slope), self.subsurfFlow)
        self.drainage = ssfConst * cos (self.slope)
        #update soil moisture
        dSoilMoist = timestep * (rainfallRate + runonRate + subsurfInflow -
                                 self.overlandFlow - self.subsurfFlow - 
                                 self.drainage)
        self.soilMoist = self.soilMoist + dSoilMoist
        #check if saturation overland flow has occurred and if so add it to HOF 
        #  and stop bucket overflow
        if (self.soilMoist > self.satSoilMoist):
            satOF = self.satSoilMoist - self.soilMoist
            self.overlandFlow = self.overlandFlow + satOF
            self.soilMoist = self.satSoilMoist
        elif (self.soilMoist < 0.):
            self.soilMoist = 1.e-6
            self.overlandFlow = 0.
        #update relative soil moisture [mm/mm]
        self.theta = self.soilMoist / self.satSoilMoist

if __name__ == '__main__':
    #simple test with constant rainfall rate
    rainfall = 20. #20 mm/h 
    finalInfiltRate = 12. #12 mm/h so should produce HOF
    soilMoist = 0.04 #assumes dry soil
    satSoilMoist = 0.38 #assumes 0.38 m/m saturated content
    transmissivity = 10.
    depth = 500.
    slope = 5.    
    #initialize simple instance of class
    soil = leakyBucket (finalInfiltRate, soilMoist, satSoilMoist,
                        transmissivity, depth, slope)
    #run storm as 60 steps of one minute each
    stormLength = 60
    timestep = 1. / 60. #in hours
    timeOut = []
    rainOut = []
    soilMoistOut = []
    overlandFlowOut = []
    subsurfFlowOut = []
    with open ("LeakyBucketResultsFile.txt", 'w') as outFile:   
        #output header
        outFile.write ("time rainfall infiltrationRate subsurfFlow " + 
                       "drainage soilMoist overlandFlow\n")

        for time in range (0, stormLength * 2):
            if time == stormLength:
                rainfall = 0.
            #update this timestep - nothing upslope so zero runon and subsurf inflow
            soil.UpdateSoilMoist (rainfall, 0., 0., timestep)
            print (time, rainfall, soil.infiltRate, soil.subsurfFlow, 
                   soil.drainage, soil.soilMoist, soil.overlandFlow)
            outFile.write (str (time) + " " + str (rainfall) + " " + 
                           str (soil.infiltRate) + " " + 
                           str (soil.subsurfFlow) + " " + 
                           str (soil.drainage) + " " + 
                           str (soil.soilMoist) + " " + 
                           str (soil.overlandFlow) + "\n")
            timeOut.append (time * timestep) #convert to h
            rainOut.append (rainfall)
            soilMoistOut.append (soil.soilMoist)
            overlandFlowOut.append (soil.overlandFlow)
            subsurfFlowOut.append (soil.subsurfFlow)
    
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
        
                        