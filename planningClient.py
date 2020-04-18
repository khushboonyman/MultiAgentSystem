import sys
import argparse
import memory
import re
from HardCoded import *
from location import *
from agent import *
from box import *
from state import State

def HandleError(message):
    print(message,file=sys.stderr,flush=True)

def ReadHeaders(messages) :
    list_of_colors = ['blue','red','cyan','purple','green','orange','pink','grey','lightblue','brown']
    line = messages.readline().rstrip()
    if line == '#domain' :
        line = messages.readline().rstrip()
        if line != 'hospital' :
            HandleError('Incorrect domain, it can only be hospital')
        else:
            ToServer('#Domain is '+line)
    else :
        HandleError('First line should be #domain') 
    
    line = messages.readline().rstrip()
    if line == '#levelname' :
        line = messages.readline().rstrip()
        ToServer('#Level name is '+line)
    else :
        HandleError('Level name is missing') 
    
    line = messages.readline().rstrip()
    if line == '#colors' :
        color_dict = {}
        while True :
            line = messages.readline().rstrip()
            color_data = re.split(', |: |\s',line)
            if color_data[0] in list_of_colors :
                if color_data[0] in color_dict.keys() :
                    HandleError('Color is repeated')
                else :
                    color_dict[color_data[0]] = color_data[1:]
            else :
                if line[0] == '#' :
                    break
                else :
                    HandleError('Unacceptable color')
    else :
        HandleError('Colors missing')
    
    if line == '#initial' :
        line = messages.readline().rstrip()
        initial_state = list()
        while line[0] == '+' :
            initial_state.append(line)
            line = messages.readline().rstrip()
    else :
        HandleError('Initial state missing')
             
    if line == '#goal' :
        line = messages.readline().rstrip()
        goal_state = list()
        while line[0] == '+' :
            goal_state.append(line)
            line = messages.readline().rstrip()
    else :
        HandleError('Goal state missing')
             
    if line != '#end' :
        HandleError('End missing')    
    
    return color_dict,initial_state,goal_state
            
def main():
    try:
        server_messages = sys.stdin
        ToServer('PlanningClient')
        color_dict,initial_state,goal_state = ReadHeaders(server_messages) 
            
    except Exception as ex:
        print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
        sys.exit(1)
                          
    HardCodedForDefault()
    State.current_state = initial_state.copy() 
    locations = set()
    agents = set()
    boxes = set()
    goals = set()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    for i_index,row in enumerate(State.current_state) :
        for j_index,col in enumerate(row) :
            loc = Location(i_index,j_index)
            locations.add(loc)
            if pattern_agent.fullmatch(col) is not None :
                for key,value in color_dict.items() :
                    if col in value :
                        agent = Agent(loc,col,key)
                        agents.add(agent)
            if pattern_box.fullmatch(col) is not None :
                for key,value in color_dict.items() :
                    if col in value :
                        box = Box(loc,col,key)
                        boxes.add(box)
            
if __name__ == '__main__':    
    # Set max memory usage allowed (soft limit).
    parser = argparse.ArgumentParser(description='Client based on planning approach.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0, help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    
    strategy_group = parser.add_mutually_exclusive_group()
    args = parser.parse_args()
    memory.max_usage = args.max_memory
    
    # Run client.
    main()

