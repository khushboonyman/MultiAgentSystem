'''
Created on Wed Apr 15 21:55:26 2020
@author :
    
change the value of global variable 'server' to True, when running using the server
When testing it with file, make it False

This will display the actions and also update current_level. At any point you can display 
current_level to see how the level looks like after any action 

'''

import argparse
from misc import memory
import re
#from box import *
#from plan import *
from state import *
import sys
from conflict import *
from setupobjects import *

x=2500
sys.setrecursionlimit(x)

<<<<<<< HEAD
def FromServer() :
    return sys.stdin.readline()

=======
global server
server = True
no_action = 'NoOp'
blocked_agents = []

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
    global blocked_agents
    plans_box = ()
    boxes = FindBox(agent.color)
    min_plan_length = State.MAX_ROW*State.MAX_COL

    if len(blocked_agents) != 0:
        for blocked_agent in blocked_agents:
            box = blocked_agent.blocked_by_box
            if agent.color == box.color:
                plan_a_b = Plan(agent.location, box.location)  # Plan for the agent to reach box
                agent_has_plan_to_box = plan_a_b.CreatePlan(agent.location, agent.location)
                if agent_has_plan_to_box:
                    plan_a_b.plan.reverse()
                    goals = FindGoal(box.color, box.letter)
                    for goal in goals:
                        plan_b_g = Plan(box.location, goal.location)  # Plan for the box to reach goal
                        box_has_plan_to_goal = plan_b_g.CreatePlan(box.location, agent.location)
                        path = []
                        if box_has_plan_to_goal:
                            plan_b_g.plan.reverse()
                            path.extend(plan_a_b.plan)
                            path.extend(plan_b_g.plan)
                            if len(path) < min_plan_length:
                                min_plan_length = len(path)
                                plans_box = (box, path)
                else:
                    blocked_agents.append(agent)

        if len(plans_box) != 0:
            blocked_agents = []
    else:
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
            else:
                agent.blocked_by_box = plan_a_b.blocked_by_box
                blocked_agents.append(agent)

    return plans_box
       
>>>>>>> 372dc30b33f63ffec7716b8b437d40638b8474ea
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
<<<<<<< HEAD
            server_messages=open('../levels/tested/SAExample.lvl','r')
        
=======
            server_messages=open('comp17/MAExample_2.lvl','r')
>>>>>>> 372dc30b33f63ffec7716b8b437d40638b8474ea
        ToServer('PlanningClient')
        #Read the input from server
        ReadHeaders(server_messages)
        
        if not server :
            server_messages.close()

    except Exception as ex:
        HandleError('PlanningClient'+str(repr(ex)))

    #Prepare objects to be used later for processing    
    SetUpObjects()    
    #Make initial pan that corresponds to the belief of the level
    MakeInitialPlan()
    #Find dependencies between goals, that is, if a goal should be achieved before another goal
    FindDependency()
    #sort the agents according to the number, so as to send their actions in the right order
    State.AgentAt.sort()
###########################################one time execution###################################################    
    count = 0 #used for testing, can be removed in the final deliverable
    
    """This gets called until every goal is reached"""
    
    while len(State.GoalLocations) > 0 and count < 50:        
        for agent in State.AgentAt :
            combined_actions = list()
            if len(agent.plan) == 0 :
                agent.MakePlan()
            #agent.CheckPlan()
            combined_actions.append(agent.Execute())
            execute = ';'.join(combined_actions)  #prepare joint actions of agents to run parallely
            ToServer(execute)
            
            if server :
                step_succeed = FromServer() #if you want to see server's response, print with a #                
        
        count+=1
        
######################################################################################################################    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')
                
                
            
            
            
        
        

