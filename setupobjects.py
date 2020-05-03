# -*- coding: utf-8 -*-
"""
Created on Sun May  3 11:56:31 2020

@author: Bruger
"""
from planningClient import *

global server
server = True

global limit #this is the limit on size of rows and columns
limit = 50

def HandleError(message):
    if server :
        print(message, file=sys.stderr, flush=True)
    else :
        print('ERROR : '+message)
    sys.exit(1)
        
def ToServer(message):
    if server :
        print(message, file=sys.stdout, flush=True)
    else :
        print(message)
        
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
        color_dict = {}
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
                color_dict[color_data[0]] = color_data[1:]
            else:
                HandleError('Unacceptable color')                   
    else:
        HandleError('Colors missing')

    if line == '#initial':
        line = Readlines(messages)
        initial_state = list()
        while line[0] != '#':
            initial_state.append(line)
            line = Readlines(messages)
    else:
        HandleError('Initial state missing')

    if line == '#goal':
        line = Readlines(messages)
        goal_state = list()
        row_index = 0
        while line[0] != '#':
            goal_state.append(line)
            if len(line) != len(initial_state[row_index]) :
                HandleError('Initial state and goal state mismatch on line '+str(row_index))
            line = Readlines(messages)
            row_index+=1
    else:
        HandleError('Goal state missing')
            
    if line != '#end':
        HandleError('End missing')

    return color_dict, initial_state, goal_state

def SetUpObjects(color_dict,goal_state) :
    State.MAX_ROW = len(State.current_level)
    if State.MAX_ROW > limit :
        HandleError('Too many rows')        
    
    State.MAX_COL = len(max(State.current_level, key=len))
    if State.MAX_COL > limit :
        HandleError('Too many columns')
        
    locations = list()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    for i_index, row in enumerate(State.current_level):
        locations_of_a_row = list()
        for j_index, col in enumerate(row):
            loc = Location(i_index, j_index)
            locations_of_a_row.append(loc)
            if col == ' ' :
                CurrentState.FreeCells.append(loc)
            if pattern_agent.fullmatch(col) is not None:
                for key, value in color_dict.items():
                    if col in value:
                        agent = Agent(loc, key, col)
                        CurrentState.AgentAt.append(agent)
            if pattern_box.fullmatch(col) is not None:
                for key, value in color_dict.items():
                    if col in value:
                        box = Box(loc, key, col)
                        CurrentState.BoxAt.append(box)
            goal = goal_state[i_index][j_index]
            if pattern_box.fullmatch(goal) is not None:
                for key, value in color_dict.items():
                    if goal in value:
                        box = Box(loc, key, goal)
                        FinalState.GoalAt.append(box)
        locations.append(locations_of_a_row)
        
    for row in range(1, State.MAX_ROW - 1):
        START_COL = State.current_level[row].index('+')+1
        END_COL = len(State.current_level[row])-1
        if START_COL < END_COL :
            for col in range(START_COL, END_COL):
                try :
                    if State.current_level[row][col] != '+' :                        
                        CurrentState.Neighbours[locations[row][col]] = set()
                        if len(State.current_level[row + 1]) > col and State.current_level[row + 1][col] != '+':
                            CurrentState.Neighbours[locations[row][col]].add(locations[row + 1][col])
                        if len(State.current_level[row - 1]) > col and State.current_level[row - 1][col] != '+':
                            CurrentState.Neighbours[locations[row][col]].add(locations[row - 1][col])
                        if State.current_level[row][col + 1] != '+':
                            CurrentState.Neighbours[locations[row][col]].add(locations[row][col + 1])
                        if State.current_level[row][col - 1] != '+':
                            CurrentState.Neighbours[locations[row][col]].add(locations[row][col - 1])
                except Exception as ex :
                    HandleError('Index row ='+str(row)+'col ='+str(col)+'/nIndex error {}'.format(repr(ex)))