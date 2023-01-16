#!/usr/bin/env python
# -*- coding: utf-8 -*-
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    call: z = merge_dicts(a, b, c, d, e, f, g) where a-g are dictionaries (can be extended unlimited: h,i,j,...)
    
    dict1 = {"key1": 10, "key2": 20, "key3": 30}
    dict2 = {"key3": 40, "key5": 50, "key6": 60}

    print(merge_dicts(dict1,dict2))
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def getClassAttributes(c):
    #get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
