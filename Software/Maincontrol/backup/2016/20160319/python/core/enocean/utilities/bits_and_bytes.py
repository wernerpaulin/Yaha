#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
