"""
Loader/parser for PRS1 family of machines.
Currently tested:
* Phillips DreamStation
"""

import struct
import numpy as np

def extract_header(rawdata):
    """
    Idx	Data		Type		Details
    00 	[02] 		8bit integer	DataFormatVersion
    01	[48 0d] 	16bit integer	BlockLength (in bytes, including header & checksum values)
    03	[00] 		8bit integer	FileType (Defining additional header information)
    04	[05] 		8bit integer	Family
    05	[00] 		8bit integer	Family Version
    06	[02] 		8bit integer	File Extension
    07	[1f 00 00 00] 	32bit integer	Session Sequence Number
    0b	[15 ae 12 4e]	32bit integer 	TimeStamp (UNIX Epoch)
    :param rawdata:
    :return:
    """
    header = {}
    header['DataVersion'] = struct.unpack("B", rawdata[0:1])[0]
    header['BlockLength'] = struct.unpack("H", rawdata[1:3])[0]
    header['FileType'] = struct.unpack("B", rawdata[3:4])[0]
    header['Family'] = struct.unpack("B", rawdata[4:5])[0]
    header['FamilyVersion'] = struct.unpack("B", rawdata[5:6])[0]
    header['FileExtension'] = struct.unpack("B", rawdata[6:7])[0]
    header['SequenceNumber'] = struct.unpack("B", rawdata[7:0x0b])[0]
    header['UnixTime'] = struct.unpack("B", rawdata[0x0b:0x0f])[0]
    return header




def extract_block(rawdata, num=100, offset=100, dtype='B'):
    step = {'B':1, 'H':2}[dtype.upper()]
    stop = offset + num*step
    section = rawdata[offset:stop]
    return list(struct.unpack('{}{}'.format(num, dtype), section))


def extract_waveform(rawdata, blocksize=1229, topheader=0x19, waveheader=0x1d):
    streams = []
    idx = 0
    trimmedData = rawdata[topheader:]
    while True:
        try:
            dd = np.array(extract_block(trimmedData, num=blocksize, offset=idx * blocksize, dtype='b'))
        except Exception:
            print('end')
            break
        dd = dd[:-waveheader]
        streams.append(dd)
        idx += 1
    return streams