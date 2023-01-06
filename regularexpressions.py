import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Dict

def is_vowel(string:str)->bool:
    if re.match(r'^[aeiouAEIOU]$',string):
        return True
    else:
        return False
def is_valid_username(string:str)->bool:
    usr_string = r'^[a-z]{1}([a-z]|[0-9]|_){,31}$'
    if re.search(usr_string,string):
        return True
    else:
        return False

def get_phone_number(string:str)->int:
    capture_str = (r'(?P<country_code>(\+1)\s?)?'
        r'\(?'
        r'(?P<area_code>[0-9]{3})'
        r'\)?'
        r'(?P<separator>[\.\-\s])?'
        r'(?P<first_three>[0-9]{3})?'
        r'(?P=separator)?'
        r'(?P<last_four>[0-9]{4}$)')
    m = re.search(capture_str,string)
    if m is None:
        return 0
    ret_no = m.group('area_code')
    if m.group('first_three') is not None:
        ret_no += m.group('first_three')
    ret_no += m.group('last_four')
    return int(ret_no)

def get_date(date_str:str)->str:
    date_cap = (
        r'(?P<month>[01][0-9])'
        r'(?P<slash>/)'
        r'(?P<day>[0-3][0-9])'
        r'(?P=slash)'
        r'(?P<year>[0-9]{2})'
        )
    months = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]
    m = re.match(date_cap,date_str)
    ret_str = m.group('day')
    ret_str += ' ' + months[int(m.group('month'))-1]
    return ret_str + ' 20' + m.group('year')

def parse_request(reqs:pd.Series)->pd.DataFrame:
    request_regex = r'''
    (?P<method>^.*?)
    \s+
    (?P<path>.*?)
    \s+
    \[(?P<timestamp>.*?)\]
    \s+
    (?P<http_version>.*?)
    \s+
    \{(?P<status>\d+0)\}
    \s+
    (?P<bytes>\d+)
    \s+
    "(?P<user_agent>.*)"
    \s+
    (?P<ip>.*)$
    '''
    return reqs.str.extract(request_regex,flags=re.VERBOSE)
    