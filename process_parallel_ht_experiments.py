#!/bin/python

import numpy as np
import pandas as pd
import re # regular expressions
import sys
import glob
import matplotlib.pyplot as plt

class TimeStepItem:
    """Class to store information about one linear step"""
    def __init__(self, number_processes):
        self.assembly_time = np.zeros((number_processes))
        self.number_of_linear_iterations = -1
        self.run_time_linear_solver = np.zeros((number_processes))

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

def tryMatchValue(line, regex, value):
    match = re.search(regex, line)
    if match:
        value = float(match.group(2))
        return int(match.group(1))
    else:
        return -1

def parseTimeStepItem(iss, time_step_item, number_processes):
    print('parseTimeStepItem')
    cnt = 0
    for line in iss:
        match = re.search('.*time.* Iteration #.* took .*', line)
        if match:
            cnt += 1
            if cnt == number_processes-1:
                return
            continue
        value = 0
        pos = tryMatchValue(line, '[(.*)] .*time.*Assembly took (.*) s', value)
        if pos != -1:
            time_step_item.assembly_time[pos] = value
        number_of_linear_iterations = tryMatch(line, '.*converged in (.*) iterations')
        if number_of_linear_iterations != -1:
            time_step_item.number_of_linear_iterations = number_of_linear_iterations
        pos = tryMatchValue(line, '[(.*)] .*time.*Linear solver took (.*) s', value)
        if pos != -1:
            time_step_item.run_time_linear_solver[pos] = value

def parseTimeStepItems(iss, time_step, number_processes):
    print('parseTimeStepItems')
    cnt_time_step_items = 0
    for line in iss:
        match = re.search('.*time.* Time step #.* took .*', line)
        if match:
            cnt_time_step_items += 1
            if cnt_time_step_items == number_processes-1:
                return
            continue
        match = re.search('.*time.* Solver step #.* took .*', line)
        if match:
            cnt_time_step_items += 1
            if cnt_time_step_items == number_processes-1:
                return
            continue
        time_step_item = TimeStepItem(number_processes)
        parseTimeStepItem(iss, time_step_item, number_processes)
        time_step.addTimeStepItem(time_step_item)

def parseTimeStep(iss, time_steps, number_processes):
    print('parseTimeStep')
    for line in iss:
        match = re.search('.*=== Time stepping at step', line)
        if match:
            time_step = TimeStep()
            parseTimeStepItems(iss, time_step, number_processes)
            time_steps.append(time_step)

time_steps = []
iss = open(sys.argv[1])
number_processes = 20
parseTimeStep(iss, time_steps, number_processes)

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
