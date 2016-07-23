'''
Created on 24.06.2014

@author: qxf5721
'''

import DyMat
import DWLibrary.SignalComparison

def main():
    reference_result_path = 'C:/Edris/EDRIS_Tools/automated_testing_EDRIS/DymolaWrapper/referenceResults/refCosine.mat'
    new_result_path = 'C:/Edris/EDRIS_Tools/automated_testing_EDRIS/DymolaWrapper/referenceResults/testCosine.mat'
    #new_result_path = 'C:/Edris/EDRIS_Tools/automated_testing_EDRIS/DymolaWrapper/referenceResults/testCosineFalse.mat'

 
    #time2=reference_result.data('Time') 
    #time1=reference_result.getTimeArray
      
    reference_result = DyMat.DymolaMat(reference_result_path)
    signal1 = reference_result.data('add.y')
    
    new_result = DyMat.DymolaMat(new_result_path)
    signal2 = new_result.data('add.y')
    
    parameters = dict()
    parameters['min_abs_tolerance'] = 0.001
    parameters['percent_tolerance'] = 0.01
    
    status = DWLibrary.SignalComparison.results_hysteresisCheck(signal1, signal2, parameters)
    #status = DWLibrary.SignalComparison.results_derivativeTest(signal1, signal2, parameters)
    
    if status is True:
        print("result is true")
    else:        
        print("result is false")


if __name__ == '__main__':
    main()