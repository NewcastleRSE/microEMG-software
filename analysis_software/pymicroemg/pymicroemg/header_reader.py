# This script is for a callable function designed to take a binary intan header file as an input
# It will return the header identifier as a check to ensure it is parsing correctly
# It will return the main version and secondary version numbers
# It will return the sample rate
# The function will throw an error if the file passed is the wrong type (expect .rdh)
# It will also check that the header ID is as expected and throw a warning if it is not.
# Callable from another file/ cmdline as import analysis
#
# FT 2024

# Library imports
import numpy as np


def header_reader(header_file):
    """
    Function for reading intan header files.
    This function expects a binary file input of format .rhd
    It will check the header id is as expected and will return
    header information, including the header ID, version number and sample rate.

    example:

    header = header_reader('header_file.rhd')

    Where the returned 'header' is a numpy array with elements:
            ("header_id", np.uint32),
            ("vnum1", np.int16),
            ("vnum2", np.int16),
            ("samprate", np.float32)

    """
    # check file type
    # try:
    #    header_file == .rdh # needs to be the last 4 characters not equal to
    # except:
    #    print('File format appears to be incorrect, have you submitted a .rdh intan header file?')

    # set the data type as per our expectations of the header file:
    dt = np.dtype(
        [
            ("header_id", np.uint32),
            ("vnum1", np.int16),
            ("vnum2", np.int16),
            ("samprate", np.float32),
        ]
    )

    # call numpy's fromfile with the above data type, for one instance of this datatype (i.e. first set of values that can be read as this dtype?)
    header = np.fromfile(header_file, dt, count=1)

    # check header ID
    if header["header_id"] != 3331401474:
        raise Exception(["Warning! The header ID is not correct for ", header_file])

    # return all the things, currently as numpy array
    return header
