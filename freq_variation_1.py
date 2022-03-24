import sys
import PyFoam

from os import path
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.Execution.BasicRunner import BasicRunner

from numpy import linspace

amp1= linspace(0.002,0.006,3)


templateCase = SolutionDirectory("pimple", archive=None, paraviewLink=False)

solver= 'pimpleFoam'

for a in amp1:
    case= templateCase.cloneCase("pimple-amp%.3f" %a)
    Newcase= "pimple-amp%.3f" %a

    velBC = ParsedParameterFile(path.join(Newcase,"0", "U"))
    velBC["boundaryField"]["auto1"]["variables"][1]= '"amp= %.3f;"'%a 
    velBC.writeFile()

    run=BasicRunner(argv=[solver,"-case",Newcase],logname="Solution")
    run.start()



#a= 0.002 #
#case= templateCase.cloneCase("pimple-amp%.3f" %a)
''' Newcase= "pimple-amp%.3f" %a
post= open(path.join(Newcase,"postProcessing", "patchAverage_massfraction","0","s"))
velBC = ParsedParameterFile(path.join(Newcase,"0", "s")) '''