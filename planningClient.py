'''
Created on Wed Apr 15 21:55:26 2020
@author :
    
change the value of global variable 'server' to True, when running using the server
When testing it with file, make it False

This will display the actions and also update State.current_level. At any point you can display 
State.current_level to see how the level looks like after any action 
'''
import random

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
# java -jar ../server.jar -l ../levels/SAFooBarSimplified_3.lvl -c "python planningClient.py" -g 150 -t 300
server = True
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

def FindGoalLocations():
    goals = set()
    for box in FinalState.GoalAt:
        goals.add(box.location)
    return goals

def MakePlan(agent):
    plans_box = ()
    boxes = FindBox(agent.color)
    min_plan_length = State.MAX_ROW*State.MAX_COL
    #to make the agent not to choose the goals as parking spot if possible
    all_goals = FindGoalLocations()
    for box in boxes :
        Plan.planning_to_goal = False #remove
        Plan.box_parking_planning=False #remove
        #resetting the parking spot?
        # Plan.
        if box.letter in Plan.parked:
            continue
        plan_a_b = Plan(agent.location, box.location, agent.color) # Plan for the agent to reach box. Added agent.color
        agent_has_plan_to_box = plan_a_b.CreatePlan(agent.location, agent.location, all_goals) #check if agent can reach box
        if agent_has_plan_to_box:
            plan_a_b.plan.reverse()
            goals = FindGoal(box.color, box.letter)
            for goal in goals :
                plan_b_g = Plan(box.location, goal.location, agent.color) # Plan for the box to reach goal    
                #we want createPlan to give us where it fails. Thus, get a tuple.
                Plan.planning_to_goal = True
                box_has_plan_to_goal = plan_b_g.CreatePlan(box.location, agent.location, all_goals) #added a goals parameter
                path = []
                # print(plan_b_g.remove_box[0])
                # print("-–––––––––––––––")
                # for i in plan_b_g.parking_spot:
                #     print(i)
                # sys.exit(1)
                if box_has_plan_to_goal :
                    plan_b_g.plan.reverse()
                    path.extend(plan_a_b.plan)
                    path.extend(plan_b_g.plan)
                    if len(path) < min_plan_length :
                        min_plan_length = len(path)
                        plans_box = (box, path)
                #if false. Call with box' goal as parking_spot. For temporary
                if not box_has_plan_to_goal:
                    Plan.box_parking_planning=True
                    #pick random from parking spot and then remove it from parking spot
                    #maybe add heuristics to the picking
                    #maybe also add the one that is closest to agent?
                    the_parking_spot = sorted(Plan.parking_spot)[0]
                    Plan.parking_spot.discard(the_parking_spot)
                    plan_b_to_parking = Plan(box.location, the_parking_spot[1], agent.color) # check how to select the parking spot
                    box_plan_to_parking_spot = plan_b_to_parking.CreatePlan(box.location, agent.location, all_goals) #added a goals parameter
                    if box_plan_to_parking_spot:
                        # Plan.parking_spot=list()
                        path.extend(plan_a_b.plan)
                        plan_b_to_parking.plan.reverse()
                        path.extend(plan_b_to_parking.plan)
                        if (len(path) < min_plan_length) and box.letter not in Plan.parked:
                            min_plan_length = len(path)
                            plans_box = (box, path)
                            Plan.parked[box.letter] = the_parking_spot
                        #Plan.parked.add(box.letter)
                    # plans_box=(box, path)
                    # Plan.parked.add(box.letter)
                    #Plan.parking_spot.remove(parking_spot) # why does the parking_spot delete one after line 87?!
                    
                    # for blockbox in Plan.remove_box:
                    #     #what if agent can't get to it?
                    #     plan_agent_to_blockbox = Plan(agent.location, blockbox, agent.color)
                    #     create_plan_agent_to_blockbox = plan_agent_to_blockbox.CreatePlan(agent.location, agent.location)
                    #     plan_move_blockbox = Plan(blockbox, Plan.parking_spot[1], agent.color)
                    #     create_plan_for_blockbox = plan_move_blockbox.CreatePlan(blockbox, agent.location)
                    #     if create_plan_for_blockbox:
                    #         path.extend(create_plan_agent_to_blockbox)
                    #         path.extend(create_plan_for_blockbox)
                    #         plans_box=(blockbox, path)

                    # return plans_box # move
                    #move the box in remove_box to free location, 
                    # and try to plan for box again
                    # while box_has_plan_to_goal is false: (not(box_has_plan_to_goal))
                    #   
                    # if solved make a dict and add the box to dict if solved. then continue and if in dict, skip it

                
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
            server_messages=open('../levels/SAFooBarSimplified_3.lvl','r')
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
    while len(FinalState.GoalAt) > 0 and count < 100: #change back to 100
        
        agent_in_conflict,location_conflict,conflict_start = None,None,None
        replan = False
        
        for agent in CurrentState.AgentAt :
            
            if replan and agent != agent_in_conflict and agent in current_plan.keys() and len(current_plan[agent][1]) > 1 :
                continue
            else :
                if agent in current_plan.keys() :
                    del current_plan[agent]
                #makes a plan for the agent
                if len(Plan.parked) == len(CurrentState.BoxAt):
                    #TODO: empty the parked.
                    Plan.parked = dict()
                    #Plan.parked=set()
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
            if execute == 'NoOp':
                if box.letter in Plan.parked:
                    del Plan.parked[box.letter]
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
                    Plan.parked.discard(box.letter)
                except Exception as ex :
                    HandleError('Key error {}'.format(repr(ex))+' for box '+str(box))

        count+=1
    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')
                
                
            
            
            
        
        

