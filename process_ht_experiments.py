#!/bin/python

import numpy as np
import pandas as pd
import re # regular expressions
import sys
import glob
import matplotlib.pyplot as plt

class TimeStepItem:
    """Class to store information about one linear step"""
    assembly_time = -1.0
    number_of_linear_iterations = -1
    run_time_linear_solver = -1.0

    def __init__(self):
        assembly_time = -1.0
        number_of_linear_iterations = -1
        run_time_linear_solver = -1.0

class TimeStep:
    """Class to store information about a time step"""
    def __init__(self):
        self.time_step_items = []

    def addTimeStepItem(self, item):
        self.time_step_items.append(item)

# reading and parsing functions
def tryMatch(line, regex):
    match = re.search(regex, line)
    if match:
        return float(match.group(1))
    else:
        return -1

def parseTimeStepItem(iss, time_step_item):
    for line in iss:
        match = re.search('info: .*time.* Iteration #.* took .*', line)
        if match:
            return
        assembly_time = tryMatch(line, '.*time.*Assembly took (.*) s')
        if assembly_time != -1.0:
            time_step_item.assembly_time = assembly_time
        number_of_linear_iterations = tryMatch(line, '.*info.*iteration: (.*)/30000')
        if number_of_linear_iterations != -1:
            time_step_item.number_of_linear_iterations = number_of_linear_iterations
        run_time_linear_solver = tryMatch(line, '.*time.*Linear solver took (.*) s')
        if run_time_linear_solver != -1.0:
            time_step_item.run_time_linear_solver = run_time_linear_solver

def parseTimeStepItems(iss, time_step):
    for line in iss:
        match = re.search('.*time.* Time step #.* took .*', line)
        if match:
            return
        match = re.search('.*time.* Solving process #', line)
        if match:
            return
        time_step_item = TimeStepItem()
        parseTimeStepItem(iss, time_step_item)
        time_step.addTimeStepItem(time_step_item)

def parseTimeStep(iss, time_steps):
    for line in iss:
        match = re.search('.*info.*=== Time stepping at step', line)
        if match:
            time_step = TimeStep()
            parseTimeStepItems(iss, time_step)
            time_steps.append(time_step)


time_steps = []
iss = open(sys.argv[1])
parseTimeStep(iss, time_steps)

print("read " + str(len(time_steps)) + " time steps")

number_time_steps = len(time_steps)
time_step_number = number_time_steps-1
time_step = time_steps[time_step_number]

for i in range(0, len(time_steps)):
    assembly_time_per_time_step = 0
    linear_solver_time_per_time_step = 0
    for j in range(0, len(time_steps[i].time_step_items)):
        assembly_time_per_time_step += time_steps[i].time_step_items[j].assembly_time
        linear_solver_time_per_time_step += time_steps[i].time_step_items[j].run_time_linear_solver
    print(str(i) + " " + str(len(time_steps[i].time_step_items)) + " " + str(assembly_time_per_time_step) + " " + str(linear_solver_time_per_time_step))
