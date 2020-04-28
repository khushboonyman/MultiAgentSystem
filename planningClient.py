'''
Created on Wed Apr 15 21:55:26 2020
@author :
    
change the value of global variable 'server' to True, when running using the server
When testing it with file, make it False

This will display the actions and also update State.current_state. At any point you can display 
State.current_state to see how the level looks like after any action 
'''

import argparse
from misc import memory
import re
from agent import *
from box import *
from plan import *
import sys
from collections import OrderedDict 

global server
server = True

def HandleError(message):
    if server :
        print(message, file=sys.stderr, flush=True)
    else :
        print('ERROR : '+message)
        
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
    added = list()
    if line == '#colors':
        color_dict = {}
        while True:
            line = Readlines(messages)
            color_data = re.split(', |: |\s', line)
            if color_data[0] in list_of_colors:
                if color_data[0] in color_dict.keys():
                    HandleError('Color is repeated')
                else:
                    for box_or_agent in color_data:
                        if box_or_agent in added:
                            HandleError('Box or agent has already been specified')
                        else:
                            added.append(box_or_agent)
                    color_dict[color_data[0]] = color_data[1:]
            else:
                if line[0] == '#':
                    break
                else:
                    HandleError('Unacceptable color')
    else:
        HandleError('Colors missing')

    if line == '#initial':
        line = Readlines(messages)
        initial_state = list()
        while line[0] == '+':
            initial_state.append(line)
            line = Readlines(messages)
    else:
        HandleError('Initial state missing')

    if line == '#goal':
        line = Readlines(messages)
        goal_state = list()
        while line[0] == '+':
            goal_state.append(line)
            line = Readlines(messages)
    else:
        HandleError('Goal state missing')

    if line != '#end':
        HandleError('End missing')

    return color_dict, initial_state, goal_state


def FindBox(color, letter):
    boxes = list()
    for box in CurrentState.BoxAt:
        if box.color == color and box.letter == letter:
            boxes.append(box)
    return boxes

def FindAgent(color):
    for agent in CurrentState.AgentAt:
        if agent.color == color:
            return agent
    return None

def SortDict(plans_box) :
    new_plan = OrderedDict()
    sortedAgents = sorted(plans_box.keys())
    for sa in sortedAgents :
        new_plan[sa] = plans_box[sa]
    return new_plan 

def MakePlan():
    plans_box = {}
    for goal in FinalState.GoalAt:
        boxes = FindBox(goal.color, goal.letter)
        agent = FindAgent(goal.color)
        if agent is not None:
            plans = list()
            for box in boxes:
                # Plan for the agent to reach box
                plan_a = Plan(agent.location, box.location)
                # Plan for the box to reach goal
                plan_b = Plan(box.location, goal.location)
                action = []
                if plan_a.CreatePlan(agent.location):
                    plan_a.plan.reverse()
                    action.extend(plan_a.plan)
                if plan_b.CreatePlan(box.location):
                    plan_b.plan.reverse()
                    action.extend(plan_b.plan)
                plans.append(action)
            index_of_box = plans.index(min(plans))
            box_chosen = boxes[index_of_box]
            plans_box[agent] = (box_chosen, min(plans))
    final_plan = SortDict(plans_box)
    return final_plan
    #return plans_box
   
    
if __name__ == '__main__':
    # Set max memory usage allowed (soft limit).
    parser = argparse.ArgumentParser(description='Client based on planning approach.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0,
                        help='The maximum memory usage allowed in MB (soft limit, default 2048).')

    strategy_group = parser.add_mutually_exclusive_group()
    args = parser.parse_args()
    memory.max_usage = args.max_memory

    # Run client.
    try:
        if server :
            server_messages = sys.stdin
        else :
            server_messages=open('../SAExample.lvl','r')
        ToServer('PlanningClient')
        color_dict, initial_state, goal_state = ReadHeaders(server_messages)
        
        if not server :
            server_messages.close()

    except Exception as ex:
        print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
        sys.exit(1)

    # below line is only for testing purpose
    # HardCodedForDefault()
    State.current_state = initial_state
    MAX_ROW = len(initial_state)
    MAX_COL = len(initial_state[0])
    locations = list()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    for i_index, row in enumerate(State.current_state):
        firstlist = list()
        for j_index, col in enumerate(row):
            loc = Location(i_index, j_index)
            firstlist.append(loc)
            if col == ' ':
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
        locations.append(firstlist)
    for row in range(1, MAX_ROW - 1):
        for col in range(1, MAX_COL - 1):
            CurrentState.Neighbours[locations[row][col]] = list()
            if State.current_state[row + 1][col] != '+':
                CurrentState.Neighbours[locations[row][col]].append(locations[row + 1][col])
            if State.current_state[row - 1][col] != '+':
                CurrentState.Neighbours[locations[row][col]].append(locations[row - 1][col])
            if State.current_state[row][col + 1] != '+':
                CurrentState.Neighbours[locations[row][col]].append(locations[row][col + 1])
            if State.current_state[row][col - 1] != '+':
                CurrentState.Neighbours[locations[row][col]].append(locations[row][col - 1])
    
    count=0
    """This needs to be called again after a plan has been executed"""
    while len(FinalState.GoalAt) > 0 and count < 10 :
        current_plan = MakePlan()
        agent_numbers = list()
        total_plan=list()
        for agent, box_cells in current_plan.items():
            box = box_cells[0]
            cells = box_cells[1]
            ##############################################
            #print('New box agent')
            #print(agent)
            #print(box)
            #for c in cells :
            #    print(c)
            ##############################################
            an_agent_box_plan = agent.ExecutePlan(box, cells, [])
            total_plan.append(an_agent_box_plan)
            agent_numbers.append(int(agent.number))
            
        execution_length = len(max(total_plan))
        total_agents = len(total_plan)
        no_action = 'NoOp'
            
        for el in range(execution_length) :
            execute = ''
            for number in range(len(CurrentState.AgentAt)) :
                if number in agent_numbers :
                    action = total_plan[number][el]
                else :
                    action = no_action
                
                if execute == '':
                    execute = execute + action
                else :
                    execute = execute + ';' + action
                
            ToServer(execute)
        
        for box in CurrentState.BoxAt :
            if box in FinalState.GoalAt :
                CurrentState.BoxAt.remove(box)
                FinalState.GoalAt.remove(box)
        count+=1
                
                
            
            
            
        
        

