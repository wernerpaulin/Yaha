#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fcntl, socket, struct

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

#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]


#get mac address of an ethernet interface
def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

 
#convert 2 byte array into 2 byte integer    
def join2BytesToInt(byteStream, endien):
    try:
        if (endien == 'big'):
            return(byteStream[0]<<8 | byteStream[1])
        else:
            return(byteStream[1]<<8 | byteStream[0])
    except:
        return(0)

#convert 4 byte array into 4 byte integer    
def join4BytesToLong(byteStream, endien):
    try:
        if (endien == 'big'):
            return(byteStream[0]<<24 | byteStream[1]<<16 | byteStream[2]<<8 | byteStream[3])
        else:
            return(byteStream[3]<<24 | byteStream[2]<<16 | byteStream[1]<<8 | byteStream[0])
    except:
        return(0)
        
#split integer into 2 bytes: higher bytes will be returned first
def splitIntIn2Bytes(intValue, endien):
    try:
        if (endien == 'big'):
            return( (int(intValue)>>8) & 0xff,  int(intValue) & 0xff )
        else:
            return( int(intValue) & 0xff, (int(intValue)>>8) & 0xff )
    except:
        return(0)
        

#split long into 4 bytes: higher bytes will be returned first
def splitLongIn4Bytes(intValue, endien):
    try:
        if (endien == 'big'):
            return( (int(intValue)>>24) & 0xff, (int(intValue)>>16) & 0xff, (int(intValue)>>8) & 0xff, int(intValue) & 0xff )
        else:
            return( int(intValue) & 0xff, (int(intValue)>>8) & 0xff, (int(intValue)>>16) & 0xff, (int(intValue)>>24) & 0xff )
    except:
        return(0)

def uniquifyList(seq, idfun=None): 
    #http://www.peterbe.com/plog/uniqifiers-benchmark    
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def optionStringToDict(optionString):
    optionDict = {'empty': 0}    #force creating a dictionary
    optionDict.clear()           #clear dictionary immediately

    #option string format: cmd:0x01 , abx:read ,
    try:
        for options in optionString.split(','):
            key = options.strip().split(':')[0]         #cmd:0x01
            value = options.strip().split(':')[1]
            optionDict[key.strip()] = value.strip()
    except:
        pass

    return optionDict
