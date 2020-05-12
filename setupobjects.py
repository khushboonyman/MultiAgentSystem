# -*- coding: utf-8 -*-
"""
Created on Sun May  3 11:56:31 2020

FUNCTIONS :
    HandleError(message)
    ToServer(message)
    Readlines(msg)
    ReadHeaders(messages)
    SetUpObjects()
    
"""
from state import *
from location import *
from agent import *
from box import *
from plan import *
from error import *
import sys
import re

#global variables
global limit, no_action  #if running from server or IDE
limit = 100

no_action = 'NoOp'
        
def Readlines(msg):
    return msg.readline().rstrip()

def ReadHeaders(messages):
    list_of_colors = ['blue', 'red', 'cyan', 'purple', 'green', 'orange', 'pink', 'grey', 'lightblue', 'brown']
    line = Readlines(messages)
    if line == '#domain':
        line = Readlines(messages)
        if line != 'hospital':
            HandleError('Incorrect domain, it can only be hospital')
        else:
            ToServer('#Domain is ' + line)
    else:
        HandleError('First line should be #domain')

    line = Readlines(messages)
    if line == '#levelname':
        line = Readlines(messages)
        ToServer('#Level name is ' + line)
    else:
        HandleError('Level name is missing')

    line = Readlines(messages)
    added = set()
    if line == '#colors':
        State.color_dict = dict()
        while True:
            line = Readlines(messages)
            if line[0] == '#' :
                break               
            color_data = re.split(', |: |\s', line)
            if color_data[0] in list_of_colors:
                for color_agent_box in color_data:
                    if color_agent_box in added:
                        HandleError('Color, agent or box has already been specified')
                    else:
                        added.add(color_agent_box)
                State.color_dict[color_data[0]] = color_data[1:]
            else:
                HandleError('Unacceptable color')                   
    else:
        HandleError('Colors missing')

    if line == '#initial':
        State.current_level = list()
        line = Readlines(messages)
        while line[0] != '#':
            State.current_level.append(line)
            line = Readlines(messages)
    else:
        HandleError('Initial state missing')

    if line == '#goal':
        line = Readlines(messages)
        State.goal_level = list()
        row_index = 0
        while line[0] != '#':
            State.goal_level.append(line)
            if len(line) != len(State.current_level[row_index]) :
                HandleError('Initial state and goal state mismatch on line '+str(row_index))
            line = Readlines(messages)
            row_index+=1
    else:
        HandleError('Goal state missing')
            
    if line != '#end':
        HandleError('End missing')
    
def SetUpObjects() :
    State.MAX_ROW = len(State.current_level)
    if State.MAX_ROW > limit :
        HandleError('Too many rows')        
    
    State.MAX_COL = len(max(State.current_level, key=len))
    if State.MAX_COL > limit :
        HandleError('Too many columns')
       
    State.Neighbours = dict() 
    State.GoalAt = dict() 
    State.Plans = dict()     
    State.AgentAt = list() 
    State.BoxAt = dict() 
    State.FreeCells = set() 
    State.GoalLocations = set()
    
    locations = list()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    for i_index, row in enumerate(State.current_level):
        locations_of_a_row = list()
        for j_index, col in enumerate(row):
            loc = Location(i_index, j_index)
            locations_of_a_row.append(loc)
            if col == ' ' :
                State.FreeCells.add(loc)
            if pattern_agent.fullmatch(col) is not None:  #making list of agents .. list(agent)
                for key, value in State.color_dict.items():
                    if col in value:
                        State.color_dict[key].remove(col)
                        agent = Agent(loc, key, col)
                        State.AgentAt.append(agent)
            if pattern_box.fullmatch(col) is not None:   #making dictionary og boxes .. {letter : list(box)}
                for key, value in State.color_dict.items():
                    if col in value:
                        box = Box(loc, key, col)
                        loc.box = box
                        if col not in State.BoxAt.keys() :
                            State.BoxAt[col] = list()
                        State.BoxAt[col].append(box)
            goal = State.goal_level[i_index][j_index]
            if pattern_box.fullmatch(goal) is not None:  #making dictionary of goals .. {letter : list(location)}
                for key, value in State.color_dict.items():
                    if goal in value:
                        if goal not in State.GoalAt.keys() :
                            State.GoalAt[goal] = list()    
                        State.GoalAt[goal].append(loc)
                        State.GoalLocations.add(loc)
        locations.append(locations_of_a_row)
        
    for row in range(1, State.MAX_ROW - 1):
        START_COL = State.current_level[row].index('+')+1
        END_COL = len(State.current_level[row])-1
        if START_COL < END_COL :
            for col in range(START_COL, END_COL):
                try :
                    if State.current_level[row][col] != '+' :                        
                        State.Neighbours[locations[row][col]] = set()
                        if len(State.current_level[row + 1]) > col and State.current_level[row + 1][col] != '+':
                            State.Neighbours[locations[row][col]].add(locations[row + 1][col])
                        if len(State.current_level[row - 1]) > col and State.current_level[row - 1][col] != '+':
                            State.Neighbours[locations[row][col]].add(locations[row - 1][col])
                        if State.current_level[row][col + 1] != '+':
                            State.Neighbours[locations[row][col]].add(locations[row][col + 1])
                        if State.current_level[row][col - 1] != '+':
                            State.Neighbours[locations[row][col]].add(locations[row][col - 1])
                except Exception as ex :
                    HandleError('SetupObjects'+' Index row ='+str(row)+'col ='+str(col)+'/nIndex error {}'.format(repr(ex)))

def MakeInitialPlan():
    for agent in State.AgentAt :
        letters = [letter for letter in State.color_dict[agent.color]]
        for letter in letters :
            boxes = State.BoxAt[letter]
            goals = State.GoalAt[letter]
        
            for box in boxes :
                plan_a_b = Plan(agent.location, box.location) # Plan for the agent to reach box
                agent_has_plan_to_box = plan_a_b.CreateBeliefPlan(agent.location)
                if agent_has_plan_to_box :
                    plan_a_b.plan.reverse()
                    State.Plans[plan_a_b] = plan_a_b.plan
                
                for goal_location in goals :
                    plan_b_g = Plan(box.location, goal_location) # Plan for the box to reach goal
                    plan_g_b = Plan(goal_location, box.location) # Plan for goal to box, could be used when agent has reached a goal and wants to go to next box
                    box_has_plan_to_goal = plan_b_g.CreateBeliefPlan(box.location)
                    if box_has_plan_to_goal :
                        plan_b_g.plan.pop(0)
                        plan_b_g.plan.append(box.location)
                        plan_g_b.plan = plan_b_g.plan.copy()
                        State.Plans[plan_g_b] = plan_g_b.plan 
                        plan_b_g.plan.pop()
                        plan_b_g.plan.reverse()
                        plan_b_g.plan.append(goal_location)
                        State.Plans[plan_b_g] = plan_b_g.plan

def FindDependency() :
    State.GoalDependency = dict()
    for plan,path in State.Plans.items() :
        if plan.end in State.GoalLocations :
            for p in path :
                if p in State.GoalLocations and p != plan.end :
                    if p not in State.GoalDependency.keys() :
                        State.GoalDependency[p] = set()
                    State.GoalDependency[p].add(plan.end)
                      