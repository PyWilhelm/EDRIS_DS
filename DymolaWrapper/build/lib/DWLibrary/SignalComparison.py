"""
Modules with methods for comparing the results from numpy
"""
import numpy as np
import matplotlib.pyplot as plt

def results_alright(reference_signal, new_result_signal, parameters):
    """ Check if the result is close enough to the reference signal using a
        simple heuristic method """
        
    average_of_two = (reference_signal + new_result_signal) / 2
    delta = reference_signal - new_result_signal
    average_non_zero = average_of_two[average_of_two > 1e-6]
    delta_at_non_zero_average = delta[average_of_two > 1e-6]

    relative_error = np.absolute(delta_at_non_zero_average / average_non_zero)
    threshold = 0.01
    print(parameters)
    if relative_error != []:
        if relative_error.max() < threshold:
            return True
        else:
            return False
    else:
        if delta.max() < threshold:
            return True
        else:
            return False
        
def results_hysteresisCheck(reference_signal, new_result_signal, parameters):
    """ Builds an Hysteresis Range over the reference result based on a given Tolarence and checks if the signal result stays inside of it """
    
    fehlerCount=0
    flag=1
    
    "Defining length of reference and result signals"
    length_reference_signal = len(reference_signal)
    length_new_result_signal = len(new_result_signal)
    
    "Definiton of the signals that will define the hysteresis Range"
    hysteresis_UP_reference_signal = [0]*length_reference_signal
    hysteresis_DOWN_reference_signal = [0]*length_reference_signal
    
    "Cheching the parameters dictionary"
    if parameters is None:
        percent_tolerance = 0.01
        min_abs_tolerance = 0.001
    else:
        percent_tolerance=parameters['percent_tolerance']
        min_abs_tolerance=parameters['min_abs_tolerance']
    
    if length_reference_signal != length_new_result_signal:
        print('Lenght Check not Passed')
        #return False
    else:
        print('Lenght Check Passed')
        #return True
    
    """Chech Algorith: It produces a given hysteretic range with a relative Tolerance as parameter.
    If the Range is smaller as a given absolute tolerance it uses the latter instead"""
    
    for i in range(0,length_reference_signal):
        if reference_signal[i] >= 0:
            if abs(reference_signal[i]*percent_tolerance) >= min_abs_tolerance:
                hysteresis_UP_reference_signal[i] = reference_signal[i] + reference_signal[i]*percent_tolerance
                hysteresis_DOWN_reference_signal[i] = reference_signal[i] - reference_signal[i]*percent_tolerance
            else:
                hysteresis_UP_reference_signal[i] = reference_signal[i] + min_abs_tolerance
                hysteresis_DOWN_reference_signal[i] = reference_signal[i] - min_abs_tolerance
        else:
            if abs(reference_signal[i]*percent_tolerance) >= min_abs_tolerance:
                hysteresis_UP_reference_signal[i] = reference_signal[i] - reference_signal[i]*percent_tolerance
                hysteresis_DOWN_reference_signal[i] = reference_signal[i] + reference_signal[i]*percent_tolerance
            else:
                hysteresis_UP_reference_signal[i] = reference_signal[i] + min_abs_tolerance
                hysteresis_DOWN_reference_signal[i] = reference_signal[i] - min_abs_tolerance
    
    """For Loop that checks if the result signal is always into the defined hysteretic Range"""
       
    for i in range(0,length_reference_signal):
        if (new_result_signal[i] < hysteresis_DOWN_reference_signal[i]) or (new_result_signal[i] > hysteresis_UP_reference_signal[i]):   
            flag=0
            fehlerCount += 1        
        else:
            pass
            
    plt.plot(reference_signal,'g',hysteresis_UP_reference_signal,'r--',hysteresis_DOWN_reference_signal,'g--')
    plt.show()
    
    print('Number of Errors:',fehlerCount)
    
    if flag == 1:
        return True
    else:
        return False
    
def results_derivativeTest(reference_signal, new_result_signal, parameters):
    """ Builds an Hysteresis Range based on the First Derivative and checks if the result stays inside of it """
    """ Function to be tested, to be used with very fast dynamic systemes """
    
    fehlerCount=0
    flag=1
    length_reference_signal = len(reference_signal)
    length_new_result_signal = len(new_result_signal)
    
    temp_reference_signal = np.delete(reference_signal,-1)   
    temp_new_result_signal = np.delete(new_result_signal,-1)
    length_temp_reference_signal = len(temp_reference_signal)
    
    derivative_reference_signal = np.diff(reference_signal)
    hysteresis_UP_reference_signal = temp_reference_signal + derivative_reference_signal
    hysteresis_DOWN_reference_signal = temp_reference_signal - derivative_reference_signal
    
    if length_reference_signal != length_new_result_signal:
        print('Lenght Check not Passed')
            #return False
    else:
        print('Lenght Check Passed')
            #return True
    
    for i in range(0,length_temp_reference_signal):
        if derivative_reference_signal[i] >= 0:
            if (temp_new_result_signal[i] < hysteresis_DOWN_reference_signal[i]) or (temp_new_result_signal[i] > hysteresis_UP_reference_signal[i]):
                flag=0
                fehlerCount += 1
            else:
                pass
        else:
            if (temp_new_result_signal[i] > hysteresis_DOWN_reference_signal[i]) or (temp_new_result_signal[i] < hysteresis_UP_reference_signal[i]):
                flag=0
                fehlerCount += 1
            else:
                pass
    #print ('Number of Errors:', fehlerCount)
    plt.plot(reference_signal,'g',hysteresis_UP_reference_signal,'r--',hysteresis_DOWN_reference_signal,'g--')
    plt.show()
    
    if flag == 1:
        return True
    else:
        return False