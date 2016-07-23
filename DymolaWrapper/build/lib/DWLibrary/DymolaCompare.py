"""
Modules for only comparing the signals
"""
import DWLibrary.DWError as EDRISError
import DWLibrary.SignalComparison as SignalComparison

def compare_all_signals(signal_list, reference_result, new_result):
    """
    Compare the result signal with the reference results saved according to
    the prefined method and parameters
    """
    for signal in signal_list:
        if signal[u'signalName'] in reference_result.names():
        
            reference_signal = reference_result.data(signal[u'signalName'])
            
            try:
                new_result_signal = new_result.data(signal[u'signalName'])
            except:
                error_message = (u'Signal ' + signal[u'signalName'] +
                                u' of the model ' +
                                " NOT FOUND!!!!!!")
                raise EDRISError.ComparisonError(error_message)                
    
            comparison_method = get_comparison_method(signal)
            parameters = get_comparison_parameters(signal)
    
            if not comparison_method(reference_signal, new_result_signal,
                                     parameters):
                error_message = (u'Signal ' + signal[u'signalName'] +
                                u' of the model ' +
    #                            model_name +
                                " has a large deviation from the reference "
                                "signal, please check if everything is ok")
                raise EDRISError.ComparisonError(error_message)
        else:
            print("Signal" + signal[u'signalName'] + " NOT FOUND in reference result") 


def get_comparison_parameters(signal):
    """ Get the parameters for signal comparison from the signal definition """
    if u"parameters" in signal.keys():
        return signal[u"parameters"]
    else:
        return None

def get_comparison_method(signal):
    """ Get the method for signal comparison from the signal definition """
    if u"method" in signal.keys():
        return getattr(SignalComparison, signal[u'signalName'])
    else:
        # default
        return getattr(SignalComparison, 'results_alright')
