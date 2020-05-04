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
server = False
no_action = 'NoOp'

def FromServer() :
    return sys.stdin.readline()

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
            server_messages=open('../levels/stupid.lvl','r')
        ToServer('PlanningClient')
        color_dict, State.current_level, goal_state = ReadHeaders(server_messages)
        
        if not server :
            server_messages.close()

    except Exception as ex:
        HandleError('Error parsing level: {}.'.format(repr(ex)))
    
    SetUpObjects(color_dict,goal_state)
###########################################one time execution###################################################    
                    
    count=0  #for testing the below line, when it runs infinitely. Needs to be removed in final execution

    total_agents = len(CurrentState.AgentAt)

    """This gets called until any goal is available"""
    
    current_plan = dict()    
    while len(FinalState.GoalAt) > 0 and count < 100:
        
        agent_in_conflict,location_conflict,conflict_start = None,None,None
        replan = False
        
        for agent in CurrentState.AgentAt :
            
            if replan and agent != agent_in_conflict and agent in current_plan.keys() and len(current_plan[agent][1]) > 1 :
                continue
            else :
                if agent in current_plan.keys() :
                    del current_plan[agent]
                #makes a plan for the agent
                plan_agent = MakePlan(agent)
                if len(plan_agent) > 0 :
                    #adds the agent and his plan to the current_plan dict()
                    current_plan[agent] = plan_agent 
            
            if agent in current_plan.keys() and len(current_plan[agent][1]) == 0:
                del current_plan[agent]
                
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
                plan = box_cells[1]
                if len(plan) > 1 :
                    next_cell = plan.pop(0)
                    next_next_cell = plan[0]
                    goal_loc = plan[-1]
                    any_plan_left = True
                    
                    if conflict and agent == agent_in_conflict and next_cell == conflict_start :
                        replan = True
                    else :
                        #PrepareAction takes one action at a time.
                        an_agent_action = agent.PrepareAction(box, next_cell, next_next_cell, goal_loc)
                        combined_actions[int(agent.number)] = an_agent_action
                    
                    if conflict and agent != agent_in_conflict and next_cell == conflict_start :
                        conflict_start = None
                        replan = True
                else :
                    
                    replan = True
                    
            if not any_plan_left :
                break
            
            execute = ';'.join(combined_actions)  #prepare joint actions of agents to run parallely
            #ToServer('#'+execute)
            ToServer(execute)
            
            if server :
                step_succeed = FromServer() #if you want to see server's response, print with a #

            if replan :   #someone needs to replan
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
                
                
            
            
            
        
        

