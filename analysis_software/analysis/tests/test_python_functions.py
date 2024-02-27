# test MatLab functions, to be compared to results given from "test_python_functions.py"

import numpy as np

# Need to add analysis folder to search path
import emg_analyser_python.emg_analyser_functions as emg

# length of vector to test
l = 70
#test vector
vec = range(1, l+1)
vec = np.array(vec)

print(vec)
print(vec.shape)

# offset
k = 2

out1 = emg.running_TEO(vec, k)

print("out1:")
print(out1)

############################
ks = [2, 3, 5]

runTEO, tmp = emg.MTEO(vec, ks)

print("out2:")
print(runTEO)


