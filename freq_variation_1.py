import sys
import PyFoam

from os import path
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.SimpleLineAnalyzer import GeneralSimpleLineAnalyzer

from numpy import linspace

amp1 = linspace(0.002, 0.006, 3)


class CompactAnalyzer(BoundingLogAnalyzer):
    def __init__(self):
        BoundingLogAnalyzer.__init__(self)
        self.addAnalyzer(
            "concentration",
            GeneralSimpleLineAnalyzer(
                "averageConcentration", "^[ ]*areaAverage\(auto2\) of s = (.+)$"
            ),
        )


templateCase = SolutionDirectory("pimple", archive=None, paraviewLink=False)

solver = "pimpleFoam"

for a in amp1:
    case = templateCase.cloneCase("pimple-amp%.3f" % a)
    Newcase = "pimple-amp%.3f" % a

    velBC = ParsedParameterFile(path.join(Newcase, "0", "U"))
    velBC["boundaryField"]["auto1"]["variables"][1] = '"amp= %.3f;"' % a
    velBC.writeFile()

    run = AnalyzedRunner(
        CompactAnalyzer(), argv=[solver, "-case", Newcase], logname="Solution",
    )
    run.start()

    times = run.getAnalyzer("concentration").lines.getTimes()
    values = run.getAnalyzer("concentration").lines.getValues("averageConcentration_0")

    # times and values are numpy arrays, you can do whatever you want here

