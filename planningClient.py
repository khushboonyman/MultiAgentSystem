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
from conflict import *
from setupobjects import *

x=2500
sys.setrecursionlimit(x)

global server
server = True

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
    min_plan_length = State.MAX_ROW*State.MAX_COL
    for box in boxes :
        plan_a_b = Plan(agent.location, box.location) # Plan for the agent to reach box
        agent_has_plan_to_box = plan_a_b.CreatePlan(agent.location, agent.location)
        if agent_has_plan_to_box :
            plan_a_b.plan.reverse()
            goals = FindGoal(box.color, box.letter)
            for goal in goals :
                plan_b_g = Plan(box.location, goal.location) # Plan for the box to reach goal    
                box_has_plan_to_goal = plan_b_g.CreatePlan(box.location, agent.location)
                path = []
                if box_has_plan_to_goal :
                    plan_b_g.plan.reverse()
                    path.extend(plan_a_b.plan)
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
    
    SetUpObjects(color_dict,goal_state)
                    
    count=0  #for testing the below line, when it runs infinitely. Needs to be removed in final execution
###########################################one time execution###################################################    
    no_action = 'NoOp'
    total_agents = len(CurrentState.AgentAt)
    """This gets called until any goal is available"""
    
    while len(FinalState.GoalAt) > 0 and count < 100:
        current_plan = dict()
        for agent in CurrentState.AgentAt :
            plan_agent = MakePlan(agent)
            if len(plan_agent) > 0 :
                current_plan[agent] = plan_agent 
        
        agent_in_conflict,location_conflict,conflict_start = None,None,None
        replan = False
        
        if len(current_plan.keys()) > 1 :
            agent_in_conflict,location_conflict,conflict_start = CheckConflict(current_plan)
        
        if agent_in_conflict is not None :
            conflict = True
        else :
            conflict = False
            
        while True :
            any_plan_left = False
            combined_actions = [no_action]*total_agents
            for agent, box_cells in current_plan.items():
                box = box_cells[0]
                cells = box_cells[1]
                if len(cells) > 1 :
                    next_cell = cells.pop(0)
                    next_next_cell = cells[0]
                    goal_loc = cells[-1]
                    any_plan_left = True
                    if conflict and agent == agent_in_conflict and next_cell == conflict_start :
                        replan = True
                    else :
                        an_agent_action = agent.PrepareAction(box, next_cell, next_next_cell, goal_loc)
                        combined_actions[int(agent.number)] = an_agent_action
                    
                    if conflict and agent != agent_in_conflict and next_cell == conflict_start :
                        conflict_start = None
                        replan = False
            if not any_plan_left :
                break
            
            execute = ';'.join(combined_actions)
            #ToServer('#'+execute)
            ToServer(execute)
            if server :
                step_succeed = FromServer()

            if replan :
                break
            
        for box in CurrentState.BoxAt :
            if box in FinalState.GoalAt :
                try :
                    FinalState.GoalAt.remove(box)
                    CurrentState.BoxAt.remove(box)
                except Exception as ex :
                    HandleError('Key error {}'.format(repr(ex))+' for box '+str(box))

        count+=1
    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')
                
                
            
            
            
        
        

