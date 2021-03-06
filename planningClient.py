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
from setupobjects import *
import globals

x=2500
sys.setrecursionlimit(x)

def FromServer() :
    return sys.stdin.readline()

if __name__ == '__main__':
    # Set max memory usage allowed (soft limit).
    parser = argparse.ArgumentParser(description='Client based on planning approach.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0,
                        help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    parser.add_argument('--server', type=bool, default=False,
                        help='The maximum memory usage allowed in MB (soft limit, default 2048).')

    args = parser.parse_args()
    memory.max_usage = args.max_memory
    globals.server = args.server

    try:
        if globals.server:
            server_messages = sys.stdin
        else :
            server_messages = open('levels/sad1k.lvl', 'r')
        ToServer('PlanningClient')
        #Read the input from server
        ReadHeaders(server_messages)
        
        if not globals.server :
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
    FindDeadCells()
###########################################one time execution###################################################    
    count = 0 #used for testing, can be removed in the final deliverable
    
    """This gets called until every goal is reached"""
    
    while len(State.GoalAt) > 0 or count < 100:
        combined_actions = list()
        agent_action = ''
        for agent in State.AgentAt :
            if len(agent.plan) == 0:
                agent.MakeDesirePlan()
            agent_action = agent.CheckAndExecute()
            combined_actions.append(agent_action)
                       
        execute = ';'.join(combined_actions)  #prepare joint actions of agents to run parallely    
        ToServer(execute)
        
        if globals.server :
            step_succeed = FromServer() #if you want to see server's response, print with a #                
            result = step_succeed.rstrip().split(';')
            if 'false' in result :
                final_combined_actions = list()
                for index,r in enumerate(result) :
                    if r == 'true' :
                        agent_action = 'NoOp'
                    else :
                        agent_action = combined_actions[index]
                    final_combined_actions.append(agent_action)
                execute = ';'.join(final_combined_actions)  #prepare joint actions of agents to run parallely    
                ToServer(execute) 
        
        count+=1
        
######################################################################################################################    
    ToServer('#Memory used ' + str(memory.get_usage()) + ' MB')

            
            
            
        
        

