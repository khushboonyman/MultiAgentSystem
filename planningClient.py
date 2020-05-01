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
from collections import OrderedDict 

x=2500
sys.setrecursionlimit(1500)

global server
server = False

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

def FromServer() :
    return sys.stdin.readline().rstrip()

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
        while line[0] != '#':
            initial_state.append(line)
            line = Readlines(messages)
    else:
        HandleError('Initial state missing')

    if line == '#goal':
        line = Readlines(messages)
        goal_state = list()
        while line[0] != '#':
            goal_state.append(line)
            line = Readlines(messages)
    else:
        HandleError('Goal state missing')

    if line != '#end':
        HandleError('End missing')

    return color_dict, initial_state, goal_state

def FindBox(color):
    boxes = list()
    for box in CurrentState.BoxAt:
        if box.color == color:
            boxes.append(box)
    return boxes

def FindGoal(color,letter):
    goals = list()
    for box in FinalState.GoalAt:
        if box.color == color and box.letter == letter:
            goals.append(box)
    return goals

def MakePlan():
    plans_box = {}
    for agent in CurrentState.AgentAt :
        boxes = FindBox(agent.color)
        min_plan_length = MAX_ROW*MAX_COL
        for box in boxes :
            goals = FindGoal(box.color, box.letter)
            for goal in goals :
                # Plan for the agent to reach box
                plan_a = Plan(agent.location, box.location)
                # Plan for the box to reach goal
                plan_b = Plan(box.location, goal.location)
                path = []
                agent_has_plan = plan_a.CreatePlan(agent.location, agent.location)
                box_has_plan = plan_b.CreatePlan(box.location, agent.location)
                if agent_has_plan and box_has_plan :
                    plan_a.plan.reverse()
                    path.extend(plan_a.plan)
                    plan_b.plan.reverse()
                    path.extend(plan_b.plan)
                if len(path) < min_plan_length and len(path) > 0 :
                    min_plan_length = len(path)
                    plan_chosen = path
                    box_chosen = box                    
                    plans_box[agent] = (box, path)
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
            server_messages=open('levels/SADangerBot.lvl','r')
        ToServer('PlanningClient')
        color_dict, initial_state, goal_state = ReadHeaders(server_messages)
        
        if not server :
            server_messages.close()

    except Exception as ex:
        print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
        sys.exit(1)

    State.current_level = initial_state
    MAX_ROW = len(initial_state)
    MAX_COL = len(max(initial_state, key=len))
    locations = list()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    for i_index, row in enumerate(State.current_level):
        initial_loc_list = list()
        for j_index, col in enumerate(row):
            loc = Location(i_index, j_index)
            initial_loc_list.append(loc)
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
        locations.append(initial_loc_list)
    for row in range(1, MAX_ROW - 1):
        START_COL = State.current_level[row].index('+')+1
        END_COL = len(State.current_level[row])-1
        if START_COL < END_COL :
            for col in range(START_COL, END_COL):
                try :
                    if State.current_level[row][col] != '+' :                        
                        CurrentState.Neighbours[locations[row][col]] = list()
                        if len(State.current_level[row + 1]) > col and State.current_level[row + 1][col] != '+':
                            CurrentState.Neighbours[locations[row][col]].append(locations[row + 1][col])
                        if len(State.current_level[row - 1]) > col and State.current_level[row - 1][col] != '+':
                            CurrentState.Neighbours[locations[row][col]].append(locations[row - 1][col])
                        if State.current_level[row][col + 1] != '+':
                            CurrentState.Neighbours[locations[row][col]].append(locations[row][col + 1])
                        if State.current_level[row][col - 1] != '+':
                            CurrentState.Neighbours[locations[row][col]].append(locations[row][col - 1])
                except Exception as ex :
                    print('Index row =',row,'col =',col,file=sys.stderr, flush=True)
                    print('Index error {}'.format(repr(ex)),file=sys.stderr, flush=True)
                    sys.exit(1)
                    
    count=0  #for testing the below line, when it runs infinitely. Needs to be removed in final execution
###########################################one time execution###################################################    
    no_action = 'NoOp'
    total_agents = len(CurrentState.AgentAt)
    """This gets called until any goal is available"""
    while len(FinalState.GoalAt) > 0 and count < 100:
        current_plan = MakePlan()
        combined_actions = [no_action]*total_agents                
        while True :
            cont = False
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
                if not step_succeed :
                    ToServer('#Failed for'+execute)
                    sys.exit(1)
        
        for box in CurrentState.BoxAt :
            if box in FinalState.GoalAt :
                CurrentState.BoxAt.remove(box)
                FinalState.GoalAt.remove(box)
        count+=1
    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')
                
                
            
            
            
        
        

