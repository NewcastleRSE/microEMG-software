# This script is for a callable function designed to take a binary intan header file as
# an input
# It will return the header identifier as a check to ensure it is parsing correctly
# It will return the main version and secondary version numbers
# It will return the sample rate
# The function will throw an error if the file passed is the wrong type (expect .rdh)
# It will also check that the header ID is as expected and throw a warning if it is not.
#
# FT 2024
# Library imports
import numpy as np


def header_reader(header_file):
    """
    Function for parsing intan header files.

    This function expects a binary file input of format .rhd
    It will check the header id is as expected and will return
    header information, including the header ID, version number and sample rate.

    Parameters
    ----------
    header_file : string
                  The file path to a binary intan header file with a .rhd format.

    Returns
    -------
    numpy array

    The returned 'header' is a numpy array with elements:
            ("header_id", np.uint32),
            ("vnum1", np.int16),
            ("vnum2", np.int16),
            ("samprate", np.float32)

    These can be accessed as array['key_value'] e.g. header['header_id']

    The different key values are as follows:

    header_id : uint32
                An ID number which should always be equal to 3331401474.
                This is in order to confirm that this is a valid intan file.

    vnum1     : int16
                The first part of the version number i.e the 1 in 1.4

    vnum2     : int16
                The second part of the version number, i.e the 4 in 1.4

    samprate  : float32
                The amplifier rate in samples/s.
                The sampling frequency of the data the file contains.


    Raises
    ------
    Excepton
        If the header ID does not match the default intan ID number.

    """
    # check file type

    if header_file.lower().endswith(".rhd"):
        pass
    else:
        print("WARNING: File extension not .rhd, have you selected the correct file?")
    # Not throwing an error here as I am unsure whether there are occasianally valid
    # header files with a different extension
    # and if they are invalid then this will be picked up with the header check or with
    # a failed file read.

    # set the data type as per our expectations of the header file:
    dt = np.dtype(
        [
            ("header_id", np.uint32),
            ("vnum1", np.int16),
            ("vnum2", np.int16),
            ("samprate", np.float32),
        ]
    )

    # call numpy's fromfile with the above data type, for one instance of this datatype
    # (i.e. first set of values that can be read as this dtype?)
    header = np.fromfile(header_file, dt, count=1)

    # check header ID
    if header["header_id"] != 3331401474:
        raise Exception(["Warning! The header ID is not correct for ", header_file])

    # return all the things, currently as numpy array
    return header
