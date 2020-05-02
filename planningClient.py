'''
Created on Wed Apr 15 21:55:26 2020
@author :
    
change the value of global variable 'server' to True, when running using the server
When testing it with file, make it False

This will display the actions and also update State.current_level. At any point you can display 
State.current_level to see how the level looks like after any action 
'''

import argparse
from misc import memory
import re
from agent import *
from box import *
from plan import *
import sys

x=2500
sys.setrecursionlimit(x)

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

def FromServer() :
    return sys.stdin.readline()

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

def FindBox(color):
    boxes = set()
    for box in CurrentState.BoxAt:
        if box.color == color:
            boxes.add(box)
    return boxes

def FindGoal(color,letter):
    goals = set()
    for box in FinalState.GoalAt:
        if box.color == color and box.letter == letter:
            goals.add(box)
    return goals

def MakePlan(agent):
    plans_box = ()
    boxes = FindBox(agent.color)
    min_plan_length = MAX_ROW*MAX_COL
    for box in boxes :
        goals = FindGoal(box.color, box.letter)
        plan_a_b = Plan(agent.location, box.location) # Plan for the agent to reach box
        agent_has_plan_to_box = plan_a_b.CreatePlan(agent.location, agent.location)
        if agent_has_plan_to_box :
            plan_a_b.plan.reverse()
            path = plan_a_b.plan
            for goal in goals :    
                plan_b_g = Plan(box.location, goal.location) # Plan for the box to reach goal    
                box_has_plan_to_goal = plan_b_g.CreatePlan(box.location, agent.location)
                if box_has_plan_to_goal :
                    plan_b_g.plan.reverse()
                    path.extend(plan_b_g.plan)
                    if len(path) < min_plan_length :
                        min_plan_length = len(path)
                        plans_box = (box, path)
    return plans_box
       
if __name__ == '__main__':
    # Set max memory usage allowed (soft limit).
    parser = argparse.ArgumentParser(description='Client based on planning approach.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0,
                        help='The maximum memory usage allowed in MB (soft limit, default 2048).')

    strategy_group = parser.add_mutually_exclusive_group()
    args = parser.parse_args()
    memory.max_usage = args.max_memory

    try:
        if server :
            server_messages = sys.stdin
        else :
            server_messages=open('levels/Tested/MAExample.lvl','r')
        ToServer('PlanningClient')
        color_dict, State.current_level, goal_state = ReadHeaders(server_messages)
        
        if not server :
            server_messages.close()

    except Exception as ex:
        HandleError('Error parsing level: {}.'.format(repr(ex)))

    MAX_ROW = len(State.current_level)
    if MAX_ROW > limit :
        HandleError('Too many rows')        
    
    MAX_COL = len(max(State.current_level, key=len))
    if MAX_COL > limit :
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
        
    for row in range(1, MAX_ROW - 1):
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
                    
    count=0  #for testing the below line, when it runs infinitely. Needs to be removed in final execution
###########################################one time execution###################################################    
    no_action = 'NoOp'
    total_agents = len(CurrentState.AgentAt)
    """This gets called until any goal is available"""
    while len(FinalState.GoalAt) > 0 and count < 100:
        current_plan = {}
        for agent in CurrentState.AgentAt :
            plan_agent = MakePlan(agent)
            if len(plan_agent) > 0 :
                current_plan[agent] = plan_agent 
            
        while True :
            cont = False
            combined_actions = [no_action]*total_agents
            for agent, box_cells in current_plan.items():
                box = box_cells[0]
                cells = box_cells[1]
                if len(cells) > 1 :
                    cell1 = cells.pop(0)
                    cell2 = cells[0]
                    goal_loc = cells[-1]
                    cont = True
                    an_agent_action = agent.PrepareAction(box, cell1, cell2, goal_loc)
                    combined_actions[int(agent.number)] = an_agent_action
            if not cont :
                break
            execute = ';'.join(combined_actions)
            ToServer(execute)
            if server :
                step_succeed = FromServer()
                joint_actions = set(combined_actions)
                if len(joint_actions) == 1 and no_action in joint_actions :
                    error = '# Failed for agents \n'
                    for a in CurrentState.AgentAt :
                        error += str(a)
                        error += '\n'
                    error += '\nboxes \n'
                    for b in CurrentState.BoxAt :
                        error += str(b)
                        error += '\n'
                    HandleError(error)
                    
        for box in CurrentState.BoxAt :
            if box in FinalState.GoalAt :
                try :
                    FinalState.GoalAt.remove(box)
                    CurrentState.BoxAt.remove(box)
                except Exception as ex :
                    HandleError('Key error {}'.format(repr(ex))+' for box '+str(box))

        count+=1
    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')
                
                
            
            
            
        
        

