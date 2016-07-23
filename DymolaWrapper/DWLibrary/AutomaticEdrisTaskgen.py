'''
Created on 11.09.2014

@author: qxb8181
'''
'''
Created on 05.09.2014

@author: qxb8181

'''



import json
import os
import re
import fnmatch
import itertools


def createJsonTests(fileName,testName,modelName,algorithm,increment,stopTime,PackagaNames):     
    
    outfile=open(fileName,'w')      
    signalNames=[]        
    testString=[]
    abc=[]    
    arg_Libs={"EDRISLibComponents","EDRISLibData","EDRISLibSystems","SimDevTools"}
    bcd={} 
    #testName='modelName'
    
    for idx1,val in enumerate(arg_Libs):  
        abc.append({"library": val})        
    
    
    for idx2,val in enumerate(modelName): 
        signalNames2=[]
        signalNames=signalNamesDef(modelName[idx2])
        
        for idx3,val in enumerate(signalNames):
            
            signalNames2.append({"signalName": val})
               
        testString.append({'testName':testName[idx2],"modelName":modelName[idx2],"simulationSettings":{"Algorithm":algorithm,"Increment":increment,"StopTime":stopTime},"results":signalNames2})  
    
    bcd["librariesRequired"]=abc
    bcd["tests"]=testString
    print((json.dumps(bcd,indent=2)))
    json.dump(bcd,outfile,indent=2) 
    
    
def raw_string(s):
    if isinstance(s, str):
        s = s.encode('string-escape')
    elif isinstance(s, str):
        s = s.encode('unicode-escape')
    return s 


def findPackageNames():
    pass


def TB_total_Search(edrisLibLoc,librarySelection):

    matches = []
    modelNames=[]
    testNames=[]
    
    searchedString=librarySelection
    modellsToTest={}
    edrisLibFolder=edrisLibLoc
    
    
    
   
        
    for root, dirnames, filenames in os.walk(edrisLibFolder):  
        
            
        #if (any("PhysicalComponents" in s for s in dirnames) or any("DymolaComponents" in s for s in dirnames)):    
        #    pass
       # else:        

            
            for filename in itertools.chain(fnmatch.filter(filenames, 'TB_*.mo') or itertools.chain(fnmatch.filter(filenames, 'TestBench_*.mo'))):
                
                #exeption added
                if re.search(r'\bPhysicalComponents\b', root) or re.search(r'\bDymolaComponents\b', root):
                   
                    pass
                else:
      
                    matches.append(os.path.join(root, filename))
                    test=os.path.join(root, filename)      
                    
                    locationOfStarting=test.rfind(searchedString)   
                   
                    
                    shortname=test[locationOfStarting:]            
                    
                      
                    modelName=shortname.replace('\\','.')
                    modelName=modelName[0:-3]    
                    
                    modelNames.append(modelName)
                    
                    #testName2=modelName[0:-3]                        
                    testName2=modelName.replace('.','_') 
                    
                    testNames.append(testName2)
                    
                    modellsToTest['modelNames']=modelNames
                    modellsToTest['testNames']=testNames
                    modellsToTest['PackageNames']='test'
                    
                    
    return modellsToTest     
   
                          
            
            
    
    



def createSignalNames(ComponentSelection,SignalBusColletction,BusNamesCollection,levelSelection):  
    SignalNames=[]
    for idx,val in enumerate(SignalBusColletction[ComponentSelection]):
            SignalNames1=[BusNamesCollection[ComponentSelection][levelSelection] + val]                            
            SignalNames=SignalNames + SignalNames1 
    return SignalNames


def signalNamesDef(ModelName): 
    SignalNames=[]   
    SignalBusColletction={}
    SubBusNamesCollection={}
    
  

    BusNamesCollection={'Batteries':{'componentLevel':{},'systemLevel':{}},
                    'Chargers':{'componentLevel':{},'systemLevel':{}},
                    'DCDCConverters':{'componentLevel':{},'systemLevel':{}},
                    'ElectricCoolers':{'componentLevel':{},'systemLevel':{}},
                    'ElectricHeaters':{'componentLevel':{},'systemLevel':{}},
                    'ElectricMachines':{'componentLevel':{},'systemLevel':{}},
                    'FuelCells':{'componentLevel':{},'systemLevel':{}},
                    'Inverters':{'componentLevel':{},'systemLevel':{}},
                    'WireHarness':{'componentLevel':{},'systemLevel':{}},
                    'SuperCap':{'componentLevel':{},'systemLevel':{}},
                    'DCLink':{'componentLevel':{},'systemLevel':{}}}



    BusNamesCollection['Batteries']['systemLevel']='batteryBus'
    BusNamesCollection['Chargers']['systemLevel']='charger1Bus'
    BusNamesCollection['DCDCConverters']['systemLevel']='dCDCConverter1Bus'
    BusNamesCollection['ElectricCoolers']['systemLevel']='electricCoolingBus'
    BusNamesCollection['ElectricHeaters']['systemLevel']='electricHeatingBus'
    BusNamesCollection['ElectricMachines']['systemLevel']='electricMachine1Bus'
    BusNamesCollection['FuelCells']['systemLevel']='fuelCellBus'
    BusNamesCollection['Inverters']['systemLevel']='inverter1Bus'
    BusNamesCollection['WireHarness']['systemLevel']='wireHarnessSetBus' 
    BusNamesCollection['SuperCap']['systemLevel']='superCap1Bus'
    BusNamesCollection['DCLink']['systemLevel']='dCLinkBus' 
    
    BusNamesCollection['Batteries']['componentLevel']='_batteryBus'
    BusNamesCollection['Chargers']['componentLevel']='_signalBus_Charger'
    BusNamesCollection['DCDCConverters']['componentLevel']='_signalBus_DCDCConverter'
    BusNamesCollection['ElectricCoolers']['componentLevel']='_signalBus_ElectricCooling'
    BusNamesCollection['ElectricHeaters']['componentLevel']='_signalBus_ElectricHeating'
    BusNamesCollection['ElectricMachines']['componentLevel']='_signalBus_ElectricMachine'
    BusNamesCollection['FuelCells']['componentLevel']='_signalBus_FuelCell'
    BusNamesCollection['Inverters']['componentLevel']='_signalBus_Inverter'
    BusNamesCollection['WireHarness']['componentLevel']='_signalBus_WireHarness' 
    BusNamesCollection['SuperCap']['componentLevel']='_signalBus_SuperCap'
    BusNamesCollection['DCLink']['componentLevel']='_signalBus_DCLink'
    
    
    
    
    
    
    
    
    SignalBusColletction['Batteries']={'.general.current','.general.voltage',
                     '.general.SOC','.general.power','.general.powerLoss',
                     '.general.voltageIdle','.thermal.temperatureCellCoreCelsius',
                     '.thermal.temperatureCellSurfaceCelsius','.controller.powerLimCharge',
                     '.controller.powerLimDischarge','.controller.currentLimCharge',
                     '.controller.currentLimDischarge','.controller.voltageLimCharge',
                     '.controller.voltageLimDischarge','.controller.RCI','.controller.boolCooling',
                     '.controller.boolHeating'}
    

    
    SignalBusColletction['Chargers']={'.general.voltageDC','.general.currentDC',
                     '.general.powerDC','.general.voltageAC',
                     '.general.currentAC','.general.powerAC',
                     '.powerLoss.powerLoss','.thermal.temperaturePowerElectronicsCelsius',
                     '.controller.currentDCLim','.controller.powerDCLim',
                     '.controller.currentDCDes','.controller.currentACLim',
                     '.controller.powerACLim'}   
        
        
    SignalBusColletction['DCDCConverters']={'.general.voltageLow','.general.voltageHigh',
                     '.general.currentLow','.general.currentHigh',
                     '.general.powerLow','.general.powerHigh',
                     '.powerLoss.powerLoss','.controller.currentLimBuck',
                     '.controller.currentLimBoost','.controller.currentSetHS',
                     '.controller.currentSetLS'}
       
    SignalBusColletction['ElectricCoolers']={'.general.voltage','.general.current',
                     '.general.powerElec','.general.COP',
                     '.thermal.powerThermal','.thermal.temperatureCoolant',
                     '.controller.boolCoolingActive'}   
    
    SignalBusColletction['ElectricHeaters']={'.general.voltage','.general.current',
                     '.general.PowerElec','.thermal.powerThermal',
                     '.thermal.temperatureCelsius','.controller.powerThermalDes'}   
    
    SignalBusColletction['ElectricMachines']={'.general.torque','.general.speed',
                     '.general.powerMech','.general.powerElec',
                     '.general.currentRMS','.general.powerFactor',
                     '.general.frequencyElec','.general.modulationIndex',
                     '.controller.torqueLimMot','.controller.torqueLimGen',
                     '.controller.speedMax','.controller.torqueLimGen',
                     '.controller.temperatureMinRotorWarningCelsius','.controller.temperatureMaxRotorWarningCelsius',
                     '.controller.temperatureMinEndwindingWarningCelsius','.controller.temperatureMaxEndwindingWarningCelsius',
                     '.powerLoss.powerLossTotal'}  
    
    SignalBusColletction['FuelCells']={'.general.voltage','.general.current',
                     '.general.voltage','.general.powerElec',
                     '.controller.powerMax',
                     '.powerLoss.powerLossPump','.powerLoss.powerLossComp',
                     '.powerLoss.powerLossTotal','.powerLoss.powerLossChem'}
    
    SignalBusColletction['Inverters']={'.general.voltageDC','.general.powerDC',
                     '.general.currentDC','.general.currentRMS',
                     '.general.powerAC','.thermal.temperatureNTCCelsius',
                     '.thermal.temperatureIGBTCelsius','.thermal.temperatureDiodeCelsius',
                     '.thermal.temperatureSolderCelsius','.controller.currentRMSLimMot',
                     '.controller.frequencySwitchingkHz','.controller.powerDCMax',
                     '.powerLoss.powerLossDiode','.powerLoss.powerLossDiodeConducting',
                     '.powerLoss.powerLossDiodeSwitching','.powerLoss.powerLossIGBT',
                     '.powerLoss.powerLossIGBTConducting','.powerLoss.powerLossIGBTSwitching',
                     '.powerLoss.powerLossTotal'}  
    
    SignalBusColletction['WireHarness']={'.general.frequency','.general.current',
                     '.general.voltageDrop','.thermal.temperatureCoreCelsius'}    
    
    SignalBusColletction['SuperCap']={'.general.current','.general.voltage','.general.power',
                     '.general.voltageIdle','.general.resistance',
                     '.general.SOC','.general.superCapMaxEnergy',
                     '.thermal.temperatureCellCelsius','.powerLoss.powerLoss'} 
    
    
    SignalBusColletction['DCLink']={'.general.voltageHVS','.general.voltageINV',
                     '.general.currentHVS','.general.currentINV',
                     '.thermal.temperatureHotspotCelsius','.powerLoss.powerLoss'}        

    
        
    
    



 


    if re.search(r'\bBatteries\b', ModelName) :                
        SignalNames=createSignalNames('Batteries',SignalBusColletction,BusNamesCollection,'componentLevel')           
    
   
    elif re.search('\bChargers\b', ModelName) :  
        SignalNames=createSignalNames('Chargers',SignalBusColletction,BusNamesCollection,'componentLevel')   
           
        
    elif re.search(r'\bDCDCConverters\b', ModelName) : 
        SignalNames=createSignalNames('DCDCConverters',SignalBusColletction,BusNamesCollection,'componentLevel')           
    
    
    elif re.search(r'\bElectricCoolers\b', ModelName) :      
        SignalNames=createSignalNames('ElectricCoolers',SignalBusColletction,BusNamesCollection,'componentLevel')   
        
    elif re.search(r'\bElectricHeaters\b', ModelName) :            
        SignalNames=createSignalNames('ElectricHeaters',SignalBusColletction,BusNamesCollection,'componentLevel')   
    
    elif re.search(r'\bElectricMachines\b', ModelName) :     
        SignalNames=createSignalNames('ElectricMachines',SignalBusColletction,BusNamesCollection,'componentLevel')   
        
    elif re.search(r'\bFuelCells\b', ModelName) :     
        SignalNames=createSignalNames('FuelCells',SignalBusColletction,BusNamesCollection,'componentLevel')           
    
    elif re.search(r'\bInverters\b', ModelName) :     
        SignalNames=createSignalNames('Inverters',SignalBusColletction,BusNamesCollection,'componentLevel')    
   
    elif re.search(r'\bWireHarness\b', ModelName) :     
        SignalNames=createSignalNames('WireHarness',SignalBusColletction,BusNamesCollection,'componentLevel')           
    
    elif re.search(r'\bSuperCap\b', ModelName) :     
        SignalNames=createSignalNames('SuperCap',SignalBusColletction,BusNamesCollection,'componentLevel')   
        
    elif re.search(r'\bDCLink\b', ModelName) :    
        SignalNames=createSignalNames('DCLink',SignalBusColletction,BusNamesCollection,'componentLevel')            
   
    elif re.search(r'\bProjects\b', ModelName) :           

        for idx,val in enumerate(SignalBusColletction): 
            
            SignalNames1=['_signalBus_Main.'+BusNamesCollection[val]['systemLevel']+old for old in SignalBusColletction[val]]     
                                   
            SignalNames=SignalNames + SignalNames1   

           
        #print SignalNames
          
    elif re.search(r'\bSystemsBases\b', ModelName) :  
            SignalNames=[]
    #else:
        #print 'Model does not exist'
    
    return SignalNames




 
    

def generate_new_tests(old_json_file, search_paths):

    # dummyjson_path = old_json_file
    newFileName='jsonAuto4.json'
    algorithm="8"
    increment="0.1"
    stopTime="5"    
    
    
    dummyjson_path = os.path.join(os.path.dirname(__file__), 'dummyJson.json')
    #modelNames = TBsearch(dummyjson_path, os.path.abspath(search_paths["EDRISLibComponents"]))
    modelNames=TB_total_Search(os.path.abspath(search_paths["EDRISLibComponents"]),'EdrisLibComponents')
    modelNames2=TB_total_Search(os.path.abspath(search_paths["EDRISLibSystems"]),'EdrisLibSystems')
    
    
    
    modelNames['testNames'] = modelNames['testNames'] + (modelNames2['testNames'])
    modelNames['modelNames']= modelNames['modelNames'] + (modelNames2['modelNames'])
    
    
   
    if not modelNames:
        print('empty file hahahaha')
    else:
        
        createJsonTests(newFileName,modelNames['testNames'],modelNames['modelNames'],algorithm,increment,stopTime,modelNames['PackageNames'])
        
        
    with open(os.path.abspath(newFileName)) as f:
        data = json.load(f)
    return data


if __name__ == '__main__': 
    generate_new_tests('temp_not_used.json', {"EDRISLibComponents" : r'C:\EdrisAscent\EdrisLibComponents_devel\branches\EA402\EdrisLibComponents',"EDRISLibSystems" : r'C:\EdrisAscent\EdrisLibSystems\trunk\EdrisLibSystems'})
