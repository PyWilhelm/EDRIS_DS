import re


def validate_sps_plot_value(userinput):
    single = 0
    multiple = 0
    error = []
    for key in userinput.keys():
        _multiple = 0
        _single = __validate_single_value(userinput[key])
        if _single == 0:
            _multiple = __validate_multiple_value(userinput[key])
        if _single + _multiple != 1:
            error.append('Input Error! %s: %s' % (key, userinput[key]))
        else:
            single += _single
            multiple += _multiple
    if multiple == 2:
        return True, None
    else:
        if len(error) == 0:
            error.append('Only two parameter can be set as variable.')
        return False, error


def __validate_single_value(value_str):
    value_str = value_str.strip()
    if value_str.find(' ') >= 0:
        return 0
    if value_str.find(':') >= 0:
        return 0
    if value_str.find(',') >= 0:
        return 0
    try:
        value_str = float(value_str)
    except:
        return 0
    return 1


def __validate_multiple_value(value_str):
    value_str = value_str.strip()
    result = re.search('^([-+]?[0-9]*\\.?[0-9]+)(:([-+]?[0-9]*\\.?[0-9]+):([-+]?[0-9]*\\.?[0-9]+))?(\\s+([-+]?[0-9]*\\.?[0-9]+)(:([-+]?[0-9]*\\.?[0-9]+):([-+]?[0-9]*\\.?[0-9]+))?)*$',
                       value_str)
    return 1 if result is None else 0

__validate_multiple_value('0:1:10')
