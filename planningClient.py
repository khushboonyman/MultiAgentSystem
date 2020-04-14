import sys
import argparse
import memory
import re
from HardCoded import *

def HandleError(message):
    print(message,file=sys.stderr,flush=True)

def ReadHeaders(messages) :
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
    
    '''line = messages.readline().rstrip()
    if line == '#colors' :
        line = messages.readline().rstrip()
        ToServer('#Level name is '+line)
    else :
        HandleError('Level name is missing') 
    '''

class PlanningClient:
    def __init__(self, server_messages):
        try:
            ToServer('PlanningClient')
            ReadHeaders(server_messages)                    
            
            linelist=list()
            line=None
            while line!='#end' :
                linelist.append(line)
                line = server_messages.readline().rstrip()
                ToServer('#'+line)
            
            HardCodedForDefault()
            #sys.exit(1)
            
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)
            
def main():
    # Read server messages from stdin.
    server_messages = sys.stdin
    client = PlanningClient(server_messages);

if __name__ == '__main__':    
    # Set max memory usage allowed (soft limit).
    parser = argparse.ArgumentParser(description='Client based on planning approach.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0, help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    
    strategy_group = parser.add_mutually_exclusive_group()
    args = parser.parse_args()
    memory.max_usage = args.max_memory
    
    # Run client.
    main()

