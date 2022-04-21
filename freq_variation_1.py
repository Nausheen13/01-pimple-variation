import sys
import PyFoam
import os
import scipy
import math
from os import path
from distutils.dir_util import copy_tree
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.SimpleLineAnalyzer import GeneralSimpleLineAnalyzer

import pandas as pd
import numpy as np
from scipy.signal import find_peaks

from numpy import linspace

amp1 = linspace(0.002, 0.006, 3)

np= 4

nt=2


class CompactAnalyzer(BoundingLogAnalyzer):
    def __init__(self):
        BoundingLogAnalyzer.__init__(self)
        self.addAnalyzer(
            "concentration",
            GeneralSimpleLineAnalyzer(
                "averageConcentration", "^[ ]*areaAverage\(auto2\) of s = (.+)$"
            ),
        )


solver = "pimpleFoam"

for a in amp1:
    os.mkdir("pimple-amp%.3f" %a)
    os.mkdir("pimple-amp%.3f/0" %a)
    os.mkdir("pimple-amp%.3f/constant" %a)
    os.mkdir("pimple-amp%.3f/system" %a)

    from_directory = "pimple/0"
    to_directory = "pimple-amp%.3f/0" %a
    copy_tree(from_directory, to_directory)

    from_directory = "pimple/constant"
    to_directory = "pimple-amp%.3f/constant" %a
    copy_tree(from_directory, to_directory)

    from_directory = "pimple/system"
    to_directory = "pimple-amp%.3f/system" %a

    copy_tree(from_directory, to_directory)

    Newcase= "pimple-amp%.3f" %a

    velBC = ParsedParameterFile(path.join(Newcase, "0", "U"))
    velBC["boundaryField"]["auto1"]["variables"][1] = '"amp= %.3f;"' % a
    velBC.writeFile()

    decomposer= UtilityRunner(
    argv=["decomposePar", "-case",Newcase],
    logname="decomposePar",
    )
    decomposer.start()

    np_substring= "mpiexec" 
    run_command = f"{np_substring} {solver} -parallel"

    run = AnalyzedRunner(
        CompactAnalyzer(), argv=[run_command, "-case", Newcase], logname="Solution",
    )
    run.start()

    times = np.array(run.getAnalyzer("concentration").lines.getTimes())
    values = np.array(run.getAnalyzer("concentration").lines.getValues("averageConcentration_0"))
    
    # times and values are numpy arrays, you can do whatever you want here

    time= np.array(times)
    value= np.array(values)

    peaks, _ = find_peaks(value, prominence=0.001)
    times_peaks = time[peaks]
    values_peaks = value[peaks]

    deltaT= np.diff(times_peaks)
    et= values_peaks/(sum(values_peaks*deltaT))

    tau= (sum(times_peaks*values_peaks*deltaT))/sum(values_peaks*deltaT)

    eteeta= tau*et
    teeta= times_peaks/tau

    min= 0
    for N in range(30,35,1):
        xy= (N*((N*teeta)**(N-1)))*(np.exp(-N*teeta))
        z= math.factorial (N-1)
        eteeta_calc= xy/z

        error_sq= sum(eteeta_calc-eteeta)

        if error_sq<min:
            min= error_sq
            N_value= N
    print(min,N)






    


