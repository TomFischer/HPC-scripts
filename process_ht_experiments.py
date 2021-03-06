#!/bin/python

import numpy as np
import re # regular expressions
import sys
import glob

class LinearStep:
    """Class to store information about one linear step"""
    assembly_time = -1.0
    number_of_linear_iterations = -1
    run_time_linear_solver = -1.0
    run_time_iteration = -1.0
    linear_step_number = -1

    def __init__(self, linearstepnumber):
        assembly_time = -1.0
        number_of_linear_iterations = -1
        run_time_linear_solver = -1.0
        run_time_iteration = -1.0
        self.linear_step_number = linearstepnumber

    def printLinearStep(self):
        print('printLinearStep:')
        print('   linear_step_number: ' + str(self.linear_step_number))
        print('   assembly: ' + str(self.assembly_time))
        print('   number_of_linear_iterations: '\
              + str(self.number_of_linear_iterations))
        print('   run_time_linear_solver: ' + str(self.run_time_linear_solver))
        print('   run_time_iteration: ' + str(self.run_time_iteration))

    def write(self):
        print(' ' + str(self.linear_step_number)
              + ' ' + str(self.assembly_time)
              + ' ' + str(self.number_of_linear_iterations)
              + ' ' + str(self.run_time_linear_solver)
              + ' ' + str(self.run_time_iteration))

    def writeAsCSV(self, time_step_number):
        print(str(time_step_number)
              + ',' + str(self.linear_step_number)
              + ',' + str(self.assembly_time)
              + ',' + str(self.number_of_linear_iterations)
              + ',' + str(self.run_time_linear_solver)
              + ',' + str(self.run_time_iteration))

    def writeCSVHeader(self):
        print('TimeStep,Iteration,AssemblyTime,NumberOfLinearSolverIterations,LinearSolverTime,IterationTime')

class TimeStep:
    """Class to store information about a time step"""
    def __init__(self, timestepnumber):
        self.linear_steps = []
        self.time_step_number = timestepnumber
        self.timestep_time = -1.0
        self.time_solving_process = -1.0
        self.output_time = -1.0

    def addLinearStep(self, item):
        self.linear_steps.append(item)

    def write(self):
        for linear_step in self.linear_steps:
            linear_step.write()
        print('+++ Time step: ' + str(self.time_step_number)
              + ' ' + str(self.time_solving_process)
              + ' ' + str(self.timestep_time)
              + ' ' + str(self.output_time))

    def writeTimestepTime(self):
        print(str(self.timestep_time))

    def writeTimestepAndOutputTime(self):
        if (self.output_time != -1.0):
            print(str(self.timestep_time + self.output_time))
        else:
            print(str(self.timestep_time))

    def writeLinearStepsAsCSV(self, time_step_number):
        for linear_step in self.linear_steps:
            linear_step.writeAsCSV(time_step_number)

# reading and parsing functions
def tryMatch(line, regex):
    match = re.search(regex, line)
    if match:
        return float(match.group(1))
    else:
        return -1

def parseLinearStep(iss, linear_step, read_line):
    assembly_time = tryMatch(read_line, '.*time.*Assembly took (.*) s')
    if assembly_time != -1.0:
        linear_step.assembly_time = assembly_time

    for line in iss:
        # print('# --- parseLinearStep: "' + line + '"')
        assembly_time = tryMatch(line, '.*time.*Assembly took (.*) s')
        if assembly_time != -1.0:
            linear_step.assembly_time = assembly_time
            continue

        number_of_linear_iterations = tryMatch(line, '.*iteration: (.*)/30000')
        if number_of_linear_iterations != -1:
            linear_step.number_of_linear_iterations = number_of_linear_iterations
            continue

        run_time_linear_solver = tryMatch(line, '.*time.*Linear solver took (.*) s')
        if run_time_linear_solver != -1.0:
            linear_step.run_time_linear_solver = run_time_linear_solver
            continue

        run_time_iteration = tryMatch(line, '.*time.* Iteration #.* took (.*) s')
        if run_time_iteration != -1.0:
            linear_step.run_time_iteration = run_time_iteration
            return
        # at the moment we don't read the convergence output

def parseLinearSteps(iss, time_step):
    linear_step_counter = 1
    for line in iss:
        time_solving_process = tryMatch(line, '.* Solving process .* took (.*) s in time step .*')
        if time_solving_process != -1.0:
            time_step.time_solving_process = time_solving_process
            continue

        timestep_time = tryMatch(line, '.* Time step .* took (.*) s.')
        if timestep_time != -1.0:
            time_step.timestep_time = timestep_time
            return

        linear_step = LinearStep(linear_step_counter)
        parseLinearStep(iss, linear_step, line)
        time_step.addLinearStep(linear_step)
        linear_step_counter = linear_step_counter + 1

def parseTimeSteps(iss, time_steps):
    for line in iss:
        time_step_number = tryMatch(line, '.*=== Time stepping at step \#(.*) and time .* with step size .*')
        if time_step_number != -1:
            time_step = TimeStep(int(time_step_number))
            parseLinearSteps(iss, time_step)
            time_steps.append(time_step)

        output_time = tryMatch(line, '.* Output of timestep .* took (.*) s')
        if output_time != -1.0:
            time_step.output_time = output_time
            continue

        match = re.search('.* The whole computation of the time stepping took .*', line)
        if match:
            return


# at the moment: jump till the Output of timestep 0
def parseInitialization(iss):
    for line in iss:
        output_time_step_zero = tryMatch(line, '.* Output of timestep 0 took (.*) s.')
        if output_time_step_zero != -1:
            return output_time_step_zero

def parseExecutionTime(iss):
    for line in iss:
        execution_time = tryMatch(line, '.* Execution took (.*) s.')
        if execution_time != -1:
            return execution_time


time_steps = []
iss = open(sys.argv[len(sys.argv)-1])
output_time_step_zero = parseInitialization(iss)
parseTimeSteps(iss, time_steps)
execution_time = parseExecutionTime(iss)

number_time_steps = len(time_steps)
time_step_number = number_time_steps-1

for arg in sys.argv:
    if (arg in ("--timestep_time")):
        for i in range(0, len(time_steps)):
            time_steps[i].writeTimestepTime()
        print("execution time " + str(execution_time))
    elif (arg in ("--output_time")):
        print(str(output_time_step_zero))
        for i in range(0, len(time_steps)):
            time_steps[i].writeTimestepAndOutputTime()
        print("execution time " + str(execution_time))
    elif (arg in ("--all")):
        print('output step zero: ' + str(output_time_step_zero))
        for i in range(0, len(time_steps)):
            time_steps[i].write()
        print("execution time " + str(execution_time))
    elif (arg in ("--linearsteps_as_csv")):
        time_steps[0].linear_steps[0].writeCSVHeader()
        for i in range(0, len(time_steps)):
            time_steps[i].writeLinearStepsAsCSV(i)
